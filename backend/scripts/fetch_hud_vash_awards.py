#!/usr/bin/env python3
"""Auto-fetch and parse HUD-VASH annual award data from PDF.

Downloads the latest HUD-VASH awards PDF from HUD.gov and extracts award data
(PHA code, name, VAMC, vouchers, budget) into the reference JSON file.

Usage:
    python scripts/fetch_hud_vash_awards.py [--year YEAR] [--output PATH] [--dry-run]

Examples:
    # Fetch 2024 awards (default)
    python scripts/fetch_hud_vash_awards.py

    # Fetch a specific year
    python scripts/fetch_hud_vash_awards.py --year 2025

    # Preview without writing
    python scripts/fetch_hud_vash_awards.py --dry-run
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

import httpx

# Optional: pdfplumber for PDF parsing
try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore[assignment]


# HUD.gov PDF URL pattern for HUD-VASH awards
# Pattern: https://www.hud.gov/sites/dfiles/PIH/documents/{YEAR}-HUD-VASH-Awards_List-by-PHA.pdf
HUD_VASH_PDF_URL_TEMPLATE = (
    "https://www.hud.gov/sites/dfiles/PIH/documents/{year}-HUD-VASH-Awards_List-by-PHA.pdf"
)

# Default output path relative to backend/
DEFAULT_OUTPUT_PATH = "data/reference/HUD_VASH_{year}_Awards.json"


@dataclass
class HUDVASHAward:
    """Represents a single HUD-VASH award entry."""

    pha_code: str
    pha_name: str
    vamc: str
    vouchers: int
    budget: int


@dataclass
class HUDVASHData:
    """Complete HUD-VASH awards data with metadata."""

    metadata: dict
    awards: list[HUDVASHAward]


def _repo_root() -> Path:
    """Find the repository root (contains 'backend' directory)."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").is_file():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[1]


def download_pdf(url: str, timeout: float = 60.0) -> bytes:
    """Download PDF from HUD.gov.

    Args:
        url: Full URL to the PDF
        timeout: Request timeout in seconds

    Returns:
        PDF content as bytes

    Raises:
        httpx.HTTPError: On download failure
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Vibe4VetsHUDVASHFetcher/1.0)",
        "Accept": "application/pdf,*/*",
    }

    with httpx.Client(follow_redirects=True, timeout=timeout) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.content


def parse_pdf_table(pdf_content: bytes) -> list[dict]:
    """Extract table data from HUD-VASH PDF.

    The PDF typically contains a table with columns:
    - PHA Code
    - PHA Name
    - VAMC
    - # Vouchers
    - Budget Authority

    Args:
        pdf_content: Raw PDF bytes

    Returns:
        List of dictionaries with extracted row data
    """
    if pdfplumber is None:
        raise ImportError(
            "pdfplumber is required for PDF parsing. "
            "Install with: pip install pdfplumber"
        )

    rows: list[dict] = []

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_content)
        tmp_path = tmp.name

    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row or len(row) < 5:
                            continue

                        # Skip header rows
                        if row[0] and "PHA" in str(row[0]).upper():
                            continue

                        parsed = _parse_table_row(row)
                        if parsed:
                            rows.append(parsed)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return rows


def _parse_table_row(row: list) -> dict | None:
    """Parse a single table row into structured data.

    Args:
        row: List of cell values from PDF table

    Returns:
        Dictionary with parsed data or None if invalid
    """
    if not row or len(row) < 5:
        return None

    # Expected columns: PHA Code, PHA Name, VAMC, Vouchers, Budget
    pha_code = _clean_text(row[0])
    pha_name = _clean_text(row[1])
    vamc = _clean_text(row[2])
    vouchers_str = _clean_text(row[3])
    budget_str = _clean_text(row[4])

    # Validate PHA code pattern (2 letters + digits)
    if not pha_code or not re.match(r"^[A-Z]{2}\d+$", pha_code):
        return None

    # Parse vouchers
    try:
        vouchers = int(vouchers_str.replace(",", ""))
    except (ValueError, AttributeError):
        return None

    # Parse budget (remove $ and commas)
    try:
        budget = int(budget_str.replace("$", "").replace(",", "").strip())
    except (ValueError, AttributeError):
        return None

    return {
        "pha_code": pha_code,
        "pha_name": pha_name,
        "vamc": vamc,
        "vouchers": vouchers,
        "budget": budget,
    }


def _clean_text(value: str | None) -> str:
    """Clean and normalize text from PDF cell.

    Args:
        value: Raw cell value

    Returns:
        Cleaned string
    """
    if value is None:
        return ""
    text = str(value).strip()
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text


def create_awards_json(
    awards: list[dict],
    year: int,
    source_url: str,
) -> dict:
    """Create the complete JSON structure for HUD-VASH awards.

    Args:
        awards: List of parsed award dictionaries
        year: Award year
        source_url: URL where PDF was fetched from

    Returns:
        Complete JSON structure with metadata
    """
    total_vouchers = sum(a["vouchers"] for a in awards)
    total_budget = sum(a["budget"] for a in awards)

    return {
        "metadata": {
            "source": source_url,
            "notice": f"PIH {year}-18",  # HUD notice number pattern
            "total_vouchers": total_vouchers,
            "total_budget": total_budget,
            "extracted_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        },
        "awards": awards,
    }


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Fetch and parse HUD-VASH annual award data from PDF."
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="Award year to fetch (default: current year)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file path (default: data/reference/HUD_VASH_{year}_Awards.json)",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Custom PDF URL (overrides year-based URL)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Download and parse but don't write output file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed progress",
    )

    args = parser.parse_args(argv)

    # Check for pdfplumber
    if pdfplumber is None:
        print("Error: pdfplumber is required for PDF parsing.")
        print("Install with: pip install pdfplumber")
        return 1

    # Determine PDF URL
    if args.url:
        pdf_url = args.url
    else:
        pdf_url = HUD_VASH_PDF_URL_TEMPLATE.format(year=args.year)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        root = _repo_root()
        output_path = root / DEFAULT_OUTPUT_PATH.format(year=args.year)

    if args.verbose:
        print(f"Fetching HUD-VASH {args.year} awards...")
        print(f"  URL: {pdf_url}")
        print(f"  Output: {output_path}")

    # Download PDF
    try:
        if args.verbose:
            print("Downloading PDF...")
        pdf_content = download_pdf(pdf_url)
        if args.verbose:
            print(f"  Downloaded {len(pdf_content):,} bytes")
    except httpx.HTTPStatusError as e:
        print(f"Error: Failed to download PDF (HTTP {e.response.status_code})")
        print(f"  URL: {pdf_url}")
        return 1
    except httpx.HTTPError as e:
        print(f"Error: Failed to download PDF: {e}")
        return 1

    # Parse PDF
    try:
        if args.verbose:
            print("Parsing PDF tables...")
        awards = parse_pdf_table(pdf_content)
        if args.verbose:
            print(f"  Extracted {len(awards)} awards")
    except Exception as e:
        print(f"Error: Failed to parse PDF: {e}")
        return 1

    if not awards:
        print("Warning: No awards extracted from PDF")
        print("The PDF structure may have changed. Check manually.")
        return 1

    # Create JSON structure
    data = create_awards_json(awards, args.year, pdf_url)

    # Summary
    print(f"\nHUD-VASH {args.year} Awards Summary:")
    print(f"  Total awards: {len(awards)}")
    print(f"  Total vouchers: {data['metadata']['total_vouchers']:,}")
    print(f"  Total budget: ${data['metadata']['total_budget']:,}")

    # Get unique states
    states = sorted({a["pha_code"][:2] for a in awards if len(a["pha_code"]) >= 2})
    print(f"  States/territories: {len(states)} ({', '.join(states[:10])}...)")

    if args.dry_run:
        print("\n[Dry run - not writing output file]")
        # Print sample of first 3 awards
        print("\nSample awards:")
        for award in awards[:3]:
            print(f"  {award['pha_code']}: {award['pha_name']} - {award['vouchers']} vouchers")
        return 0

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nWrote: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
