#!/usr/bin/env python3
"""Synchronous scraper for LSC grantee contact info - more reliable than async."""

import re
import sys
from pathlib import Path

import httpx
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PHONE_PATTERNS = [
    r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    r"1[-.\s]?8[0-9]{2}[-.\s]?\d{3}[-.\s]?\d{4}",
]


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone


def extract_phones(text: str) -> list[str]:
    phones = []
    for pattern in PHONE_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            normalized = normalize_phone(match)
            if normalized not in phones:
                phones.append(normalized)
    return phones


def clean_html(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text)


def scrape_site(url: str, timeout: float = 10.0) -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text
    except Exception:
        return None


def get_phone(website: str) -> str | None:
    html = scrape_site(website)
    if not html:
        return None

    text = clean_html(html)
    phones = extract_phones(text)

    if phones:
        toll_free = [p for p in phones if p.startswith("(8")]
        return toll_free[0] if toll_free else phones[0]

    # Try contact page
    for path in ["/contact", "/contact-us"]:
        html = scrape_site(website.rstrip("/") + path)
        if html:
            phones = extract_phones(clean_html(html))
            if phones:
                toll_free = [p for p in phones if p.startswith("(8")]
                return toll_free[0] if toll_free else phones[0]

    return None


def main():
    yaml_path = PROJECT_ROOT / "data/reference/lsc_grantees.yaml"

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    grantees = data.get("grantees", [])
    updated = 0

    for i, g in enumerate(grantees):
        name = g["name"]
        website = g.get("website")

        # Skip if already has phone or no website
        if g.get("phone") or not website:
            continue

        print(f"[{i+1}/{len(grantees)}] {name}...", end=" ", flush=True)

        phone = get_phone(website)
        if phone:
            g["phone"] = phone
            updated += 1
            print(f"✓ {phone}")
        else:
            print("✗")

    # Save
    with open(yaml_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\nUpdated {updated} entries")


if __name__ == "__main__":
    main()
