#!/usr/bin/env python3
"""Fetch PHA (Public Housing Authority) contact information from HUD.gov.

Downloads state-specific PHA Contact Report PDFs from HUD.gov and extracts
contact information (phone numbers, addresses, emails) for each PHA.

The extracted data is used to enrich HUD-VASH resources with contact information
so veterans can actually reach their local PHA to apply for housing vouchers.

Source: https://www.hud.gov/program_offices/public_indian_housing/pha/contacts
PDF Pattern: https://www.hud.gov/sites/dfiles/PIH/documents/PHA_Contact_Report_{STATE}.pdf

Usage:
    python scripts/fetch_pha_contacts.py [--output PATH] [--states STATE1,STATE2] [--dry-run]

Examples:
    # Fetch contacts for all states
    python scripts/fetch_pha_contacts.py

    # Fetch specific states
    python scripts/fetch_pha_contacts.py --states TX,CA,FL

    # Preview without writing
    python scripts/fetch_pha_contacts.py --dry-run --states TX
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

import httpx

# Optional: pdfplumber for PDF parsing
try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore[assignment]


# PDF URL pattern
PHA_CONTACT_PDF_URL_PATTERN = (
    "https://www.hud.gov/sites/dfiles/PIH/documents/PHA_Contact_Report_{state}.pdf"
)

# Default output path
DEFAULT_OUTPUT_PATH = "data/reference/PHA_Contacts.json"

# All US states and territories with potential PHAs
ALL_STATES = [
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL",
    "GA", "GQ", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA",
    "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND",
    "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA",
    "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VI", "VT",
    "WA", "WI", "WV", "WY",
]


@dataclass
class PHAContact:
    """Contact information for a Public Housing Authority."""

    pha_code: str
    pha_name: str
    phone: str | None = None
    fax: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    executive_director: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary, omitting None values."""
        return {k: v for k, v in {
            "pha_code": self.pha_code,
            "pha_name": self.pha_name,
            "phone": self.phone,
            "fax": self.fax,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "executive_director": self.executive_director,
        }.items() if v is not None}


def _repo_root() -> Path:
    """Find the repository root."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").is_file():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[1]


def download_pdf(url: str, timeout: float = 60.0) -> bytes | None:
    """Download PDF from HUD.gov.

    Args:
        url: Full URL to the PDF
        timeout: Request timeout in seconds

    Returns:
        PDF content as bytes, or None if not found (404)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Vibe4VetsPHAFetcher/1.0)",
        "Accept": "application/pdf,*/*",
    }

    with httpx.Client(follow_redirects=True, timeout=timeout) as client:
        response = client.get(url, headers=headers)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.content


def parse_pha_contact_pdf(pdf_content: bytes, state: str) -> list[PHAContact]:
    """Parse a state's PHA Contact Report PDF.

    HUD PHA Contact PDFs have an unusual layout where each row contains:
    - Column 0: PHA Code (e.g., "TX064")
    - Column 1: PHA Name + Phone + Fax + Email (all in one cell with newlines)
    - Column 2: Physical Address (street, city, state, zip on multiple lines)
    - Column 3: Type (Combined, Low-Rent, etc.)

    Args:
        pdf_content: Raw PDF bytes
        state: State code for context

    Returns:
        List of PHAContact objects
    """
    if pdfplumber is None:
        raise ImportError(
            "pdfplumber is required for PDF parsing. "
            "Install with: pip install pdfplumber"
        )

    contacts: list[PHAContact] = []

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_content)
        tmp_path = tmp.name

    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue

                    for row in table:
                        if not row:
                            continue

                        # Skip header rows
                        if _is_contact_header_row(row):
                            continue

                        # Parse HUD-format data rows
                        contact = _parse_hud_contact_row(row, state)
                        if contact:
                            contacts.append(contact)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return contacts


def _is_contact_header_row(row: list) -> bool:
    """Check if row is a header row containing column names."""
    if not row or len(row) < 2:
        return False

    # Look for typical header values
    text = " ".join(str(cell or "").upper() for cell in row[:5])
    return ("PHA CODE" in text or "PHA #" in text) and ("NAME" in text or "PHONE" in text)


def _parse_hud_contact_row(row: list, default_state: str) -> PHAContact | None:
    """Parse a HUD-format contact row.

    HUD PHA Contact Report rows contain:
    - Column 0: PHA Code (e.g., "TX064")
    - Column 1: PHA Name + Contact info (name, phone, fax, email on separate lines)
    - Column 2: Physical Address (street, city, state, zip on multiple lines)
    - Column 3: Type (Combined, Low-Rent, etc.)

    Args:
        row: Data row from PDF table
        default_state: State code for context

    Returns:
        PHAContact object or None if invalid
    """
    if not row or len(row) < 2:
        return None

    # Column 0: PHA Code
    pha_code = str(row[0] or "").strip()
    if not pha_code or not re.match(r"^[A-Z]{2}\d+$", pha_code, re.IGNORECASE):
        return None

    # Column 1: Name + Contact Info (multi-line cell)
    name_cell = str(row[1] or "") if len(row) > 1 else ""
    if not name_cell:
        return None

    # Parse the name/contact cell
    pha_name = None
    phone = None
    fax = None
    email = None

    lines = name_cell.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for Phone:, Fax:, Email: prefixes
        line_lower = line.lower()
        if line_lower.startswith("phone:"):
            phone = _normalize_phone(line[6:].strip())
        elif line_lower.startswith("fax:"):
            fax = _normalize_phone(line[4:].strip())
        elif line_lower.startswith("email:"):
            email = line[6:].strip()
        elif pha_name is None:
            # First non-prefixed line is the PHA name
            pha_name = line

    if not pha_name:
        return None

    # Column 2: Address (multi-line)
    address = None
    city = None
    state = default_state
    zip_code = None

    if len(row) > 2 and row[2]:
        addr_cell = str(row[2])
        addr_lines = [l.strip() for l in addr_cell.split("\n") if l.strip()]

        if addr_lines:
            # First line is usually street address
            address = addr_lines[0]

            # Look for city and state/zip
            for line in addr_lines[1:]:
                # Pattern: "CITY" or "TX , 78516" or "city\nTX , zip"
                zip_match = re.search(r"([A-Z]{2})\s*,?\s*(\d{5}(?:-\d{4})?)", line)
                if zip_match:
                    state = zip_match.group(1)
                    zip_code = zip_match.group(2)
                    # City is everything before the state/zip
                    city_part = line[:zip_match.start()].strip().rstrip(",")
                    if city_part:
                        city = city_part
                elif not city and line and not re.match(r"^[A-Z]{2}\s*,", line):
                    # This is probably the city
                    city = line

    return PHAContact(
        pha_code=pha_code.upper(),
        pha_name=pha_name,
        phone=phone,
        fax=fax,
        email=email,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
    )


def _normalize_phone(phone: str) -> str | None:
    """Normalize phone number to consistent format.

    Args:
        phone: Raw phone string

    Returns:
        Normalized phone or None if invalid
    """
    # Extract just digits
    digits = re.sub(r"\D", "", phone)

    # Handle 10-digit US numbers
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    # Handle 11-digit with leading 1
    if len(digits) == 11 and digits[0] == "1":
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

    # Return original if can't normalize
    if len(digits) >= 7:
        return phone.strip()

    return None


def fetch_all_pha_contacts(
    states: list[str] | None = None,
    verbose: bool = False,
) -> dict[str, PHAContact]:
    """Fetch PHA contacts for all specified states.

    Args:
        states: List of state codes, or None for all states
        verbose: Print progress

    Returns:
        Dictionary mapping PHA code to PHAContact
    """
    if states is None:
        states = ALL_STATES

    all_contacts: dict[str, PHAContact] = {}
    successful_states = 0
    failed_states = []

    for i, state in enumerate(states):
        url = PHA_CONTACT_PDF_URL_PATTERN.format(state=state)

        if verbose:
            print(f"[{i + 1}/{len(states)}] Fetching {state}...")

        try:
            pdf_content = download_pdf(url)

            if pdf_content is None:
                if verbose:
                    print(f"  -> Not found (404)")
                failed_states.append(state)
                continue

            contacts = parse_pha_contact_pdf(pdf_content, state)

            for contact in contacts:
                # Use PHA code as key, update if exists
                all_contacts[contact.pha_code] = contact

            successful_states += 1
            if verbose:
                print(f"  -> Found {len(contacts)} PHAs")

        except httpx.HTTPError as e:
            if verbose:
                print(f"  -> HTTP error: {e}")
            failed_states.append(state)

        except Exception as e:
            if verbose:
                print(f"  -> Parse error: {e}")
            failed_states.append(state)

        # Be polite to HUD servers
        if i < len(states) - 1:
            sleep(0.5)

    if verbose:
        print(f"\nFetched {successful_states}/{len(states)} states")
        print(f"Total unique PHAs: {len(all_contacts)}")
        if failed_states:
            print(f"Failed states: {', '.join(failed_states)}")

    return all_contacts


def create_contacts_json(
    contacts: dict[str, PHAContact],
    source_url_pattern: str,
) -> dict:
    """Create JSON structure from contacts.

    Args:
        contacts: Dictionary of contacts
        source_url_pattern: URL pattern used

    Returns:
        Complete JSON structure
    """
    # Get unique states
    states_with_contacts = sorted({
        c.state for c in contacts.values() if c.state
    })

    # Count contacts with phone numbers
    with_phone = sum(1 for c in contacts.values() if c.phone)

    return {
        "metadata": {
            "source": "HUD.gov PHA Contact Reports",
            "source_url_pattern": source_url_pattern,
            "description": "Public Housing Authority contact information by state",
            "total_phas": len(contacts),
            "phas_with_phone": with_phone,
            "states_covered": states_with_contacts,
            "extracted_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        },
        "contacts": {
            code: contact.to_dict()
            for code, contact in sorted(contacts.items())
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch PHA contact information from HUD.gov PDFs."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Output JSON file (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--states",
        type=str,
        default=None,
        help="Comma-separated state codes (default: all states)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and parse but don't write output",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )

    args = parser.parse_args(argv)

    if pdfplumber is None:
        print("Error: pdfplumber is required for PDF parsing.")
        print("Install with: pip install pdfplumber")
        return 1

    # Parse states
    states = None
    if args.states:
        states = [s.strip().upper() for s in args.states.split(",")]
        invalid = [s for s in states if s not in ALL_STATES]
        if invalid:
            print(f"Warning: Unknown state codes: {', '.join(invalid)}")

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        root = _repo_root()
        output_path = root / DEFAULT_OUTPUT_PATH

    if args.verbose:
        print(f"Fetching PHA contact information...")
        print(f"  States: {', '.join(states) if states else 'All'}")
        print(f"  Output: {output_path}")

    # Fetch contacts
    contacts = fetch_all_pha_contacts(states=states, verbose=args.verbose)

    if not contacts:
        print("Warning: No contacts extracted")
        return 1

    # Create JSON structure
    data = create_contacts_json(contacts, PHA_CONTACT_PDF_URL_PATTERN)

    # Summary
    print(f"\nPHA Contact Summary:")
    print(f"  Total PHAs: {len(contacts)}")
    print(f"  With phone: {data['metadata']['phas_with_phone']}")
    print(f"  States: {len(data['metadata']['states_covered'])}")

    if args.verbose:
        # Show sample contacts
        print("\nSample contacts:")
        for code in list(sorted(contacts.keys()))[:5]:
            c = contacts[code]
            print(f"  {c.pha_code}: {c.pha_name}")
            if c.phone:
                print(f"    Phone: {c.phone}")
            if c.city:
                print(f"    City: {c.city}, {c.state}")

    if args.dry_run:
        print("\n[Dry run - not writing output file]")
        return 0

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nWrote: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
