#!/usr/bin/env python3
"""Fetch and merge multi-year HUD-VASH award data.

Downloads the comprehensive HUD-VASH awards PDF (2008-2024) from HUD.gov and
extracts cumulative award data per PHA across all years.

This creates a merged dataset that provides:
- Comprehensive state coverage (more PHAs than single-year data)
- Historical award tracking per PHA
- Total vouchers allocated over time

Usage:
    python scripts/fetch_hud_vash_multiyear.py [--output PATH] [--dry-run]

Examples:
    # Fetch and merge all years
    python scripts/fetch_hud_vash_multiyear.py

    # Preview without writing
    python scripts/fetch_hud_vash_multiyear.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx

# Optional: pdfplumber for PDF parsing
try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore[assignment]


# Comprehensive HUD-VASH awards PDF (2008-2024)
HUD_VASH_MULTIYEAR_PDF_URL = (
    "https://www.hud.gov/sites/dfiles/PIH/documents/HUD-VASH-Awards.pdf"
)

# Default output path
DEFAULT_OUTPUT_PATH = "data/reference/HUD_VASH_All_Years.json"

# Years we want to extract (recent years for relevance)
TARGET_YEARS = [2020, 2021, 2022, 2023, 2024]


@dataclass
class PHAAward:
    """Represents a PHA with awards across multiple years."""

    pha_code: str
    pha_name: str
    awards_by_year: dict[int, int] = field(default_factory=dict)
    total_vouchers: int = 0

    def add_year(self, year: int, vouchers: int) -> None:
        """Add vouchers for a specific year."""
        if vouchers > 0:
            self.awards_by_year[year] = vouchers
            self.total_vouchers += vouchers


def _repo_root() -> Path:
    """Find the repository root."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").is_file():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[1]


def download_pdf(url: str, timeout: float = 120.0) -> bytes:
    """Download PDF from HUD.gov.

    Args:
        url: Full URL to the PDF
        timeout: Request timeout in seconds

    Returns:
        PDF content as bytes
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Vibe4VetsHUDVASHFetcher/1.0)",
        "Accept": "application/pdf,*/*",
    }

    with httpx.Client(follow_redirects=True, timeout=timeout) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.content


def parse_multiyear_pdf(pdf_content: bytes) -> dict[str, PHAAward]:
    """Parse the comprehensive multi-year HUD-VASH PDF.

    The PDF contains a table with columns:
    - PHA # (code)
    - PHA Name
    - Multiple year columns (FY2008, FY2009, ..., FY2024)
    - PBV Set-Aside Awards columns
    - Total column

    Args:
        pdf_content: Raw PDF bytes

    Returns:
        Dictionary mapping PHA code to PHAAward object
    """
    if pdfplumber is None:
        raise ImportError(
            "pdfplumber is required for PDF parsing. "
            "Install with: pip install pdfplumber"
        )

    phas: dict[str, PHAAward] = {}

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_content)
        tmp_path = tmp.name

    try:
        with pdfplumber.open(tmp_path) as pdf:
            # First, find the header row to identify year columns
            year_columns: dict[int, int] = {}  # year -> column index

            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue

                    # Look for header row with year columns
                    for row in table:
                        if not row:
                            continue

                        # Check if this is the header row
                        if _is_header_row(row):
                            year_columns = _extract_year_columns(row)
                            continue

                        # Parse data rows
                        if year_columns and len(row) >= 3:
                            pha = _parse_multiyear_row(row, year_columns)
                            if pha:
                                # Merge with existing if same PHA code
                                if pha.pha_code in phas:
                                    existing = phas[pha.pha_code]
                                    for year, vouchers in pha.awards_by_year.items():
                                        existing.add_year(year, vouchers)
                                else:
                                    phas[pha.pha_code] = pha
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return phas


def _is_header_row(row: list) -> bool:
    """Check if row is a header row containing column names."""
    if not row or len(row) < 3:
        return False

    first_cell = str(row[0] or "").upper()
    return "PHA" in first_cell and ("#" in first_cell or "CODE" in first_cell or "NAME" in str(row[1] or "").upper())


def _extract_year_columns(row: list) -> dict[int, int]:
    """Extract year column indices from header row.

    Args:
        row: Header row

    Returns:
        Dict mapping year to column index
    """
    year_columns: dict[int, int] = {}

    for idx, cell in enumerate(row):
        if cell is None:
            continue

        cell_str = str(cell).strip().upper()

        # Look for FY20XX or 20XX patterns
        match = re.search(r"(?:FY)?(\d{4})", cell_str)
        if match:
            year = int(match.group(1))
            if 2008 <= year <= 2030:  # Reasonable year range
                year_columns[year] = idx

    return year_columns


def _parse_multiyear_row(row: list, year_columns: dict[int, int]) -> PHAAward | None:
    """Parse a data row from the multi-year table.

    Args:
        row: Data row
        year_columns: Mapping of year to column index

    Returns:
        PHAAward object or None if invalid
    """
    if not row or len(row) < 3:
        return None

    # First two columns are PHA code and name
    pha_code = _clean_text(row[0])
    pha_name = _clean_text(row[1])

    # Validate PHA code (2 letters + digits)
    if not pha_code or not re.match(r"^[A-Z]{2}\d+$", pha_code):
        return None

    if not pha_name:
        return None

    pha = PHAAward(pha_code=pha_code, pha_name=pha_name)

    # Extract awards for each target year
    for year in TARGET_YEARS:
        if year not in year_columns:
            continue

        col_idx = year_columns[year]
        if col_idx >= len(row):
            continue

        cell = row[col_idx]
        vouchers = _parse_voucher_count(cell)
        if vouchers > 0:
            pha.add_year(year, vouchers)

    # Only return if we have at least one year of data
    if pha.awards_by_year:
        return pha

    return None


def _parse_voucher_count(cell: str | None) -> int:
    """Parse voucher count from cell value.

    Args:
        cell: Cell value

    Returns:
        Integer voucher count or 0
    """
    if cell is None:
        return 0

    text = str(cell).strip()
    if not text or text == "-" or text.lower() == "n/a":
        return 0

    # Remove commas and try to parse
    try:
        return int(text.replace(",", ""))
    except ValueError:
        return 0


def _clean_text(value: str | None) -> str:
    """Clean and normalize text from PDF cell."""
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def create_merged_json(phas: dict[str, PHAAward], source_url: str) -> dict:
    """Create merged JSON structure from multi-year data.

    Args:
        phas: Dictionary of PHA awards
        source_url: Source PDF URL

    Returns:
        Complete JSON structure
    """
    # Calculate totals by year
    totals_by_year: dict[int, int] = {year: 0 for year in TARGET_YEARS}
    for pha in phas.values():
        for year, vouchers in pha.awards_by_year.items():
            if year in totals_by_year:
                totals_by_year[year] += vouchers

    # Create awards list sorted by PHA code
    awards = []
    for pha_code in sorted(phas.keys()):
        pha = phas[pha_code]
        awards.append({
            "pha_code": pha.pha_code,
            "pha_name": pha.pha_name,
            "awards_by_year": pha.awards_by_year,
            "total_vouchers": pha.total_vouchers,
        })

    # Get unique states
    states = sorted({pha.pha_code[:2] for pha in phas.values() if len(pha.pha_code) >= 2})

    return {
        "metadata": {
            "source": source_url,
            "description": "HUD-VASH voucher awards by PHA across multiple fiscal years",
            "years_included": TARGET_YEARS,
            "totals_by_year": totals_by_year,
            "total_phas": len(awards),
            "states_covered": states,
            "extracted_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        },
        "awards": awards,
    }


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch and merge multi-year HUD-VASH award data."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Output JSON file (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=HUD_VASH_MULTIYEAR_PDF_URL,
        help="PDF URL to fetch",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Download and parse but don't write output",
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

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        root = _repo_root()
        output_path = root / DEFAULT_OUTPUT_PATH

    if args.verbose:
        print(f"Fetching multi-year HUD-VASH awards...")
        print(f"  URL: {args.url}")
        print(f"  Output: {output_path}")
        print(f"  Target years: {TARGET_YEARS}")

    # Download PDF
    try:
        if args.verbose:
            print("Downloading PDF...")
        pdf_content = download_pdf(args.url)
        if args.verbose:
            print(f"  Downloaded {len(pdf_content):,} bytes")
    except httpx.HTTPStatusError as e:
        print(f"Error: Failed to download PDF (HTTP {e.response.status_code})")
        return 1
    except httpx.HTTPError as e:
        print(f"Error: Failed to download PDF: {e}")
        return 1

    # Parse PDF
    try:
        if args.verbose:
            print("Parsing multi-year PDF tables...")
        phas = parse_multiyear_pdf(pdf_content)
        if args.verbose:
            print(f"  Extracted {len(phas)} unique PHAs")
    except Exception as e:
        print(f"Error: Failed to parse PDF: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if not phas:
        print("Warning: No awards extracted from PDF")
        print("The PDF structure may have changed.")
        return 1

    # Create JSON structure
    data = create_merged_json(phas, args.url)

    # Summary
    print(f"\nHUD-VASH Multi-Year Awards Summary:")
    print(f"  Total unique PHAs: {len(phas)}")
    print(f"  States/territories: {len(data['metadata']['states_covered'])}")
    print(f"  Years: {TARGET_YEARS}")
    print("\n  Vouchers by year:")
    for year, total in sorted(data["metadata"]["totals_by_year"].items()):
        print(f"    FY{year}: {total:,} vouchers")

    total_all = sum(pha.total_vouchers for pha in phas.values())
    print(f"  Total (all years): {total_all:,} vouchers")

    if args.dry_run:
        print("\n[Dry run - not writing output file]")
        print("\nSample PHAs:")
        for award in data["awards"][:5]:
            years_str = ", ".join(f"FY{y}: {v}" for y, v in sorted(award["awards_by_year"].items()))
            print(f"  {award['pha_code']}: {award['pha_name']}")
            print(f"    {years_str}")
        return 0

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nWrote: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
