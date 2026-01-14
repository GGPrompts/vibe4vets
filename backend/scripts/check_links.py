#!/usr/bin/env python3
"""Check curated external links for obvious breakage (404/5xx/timeouts).

Intended for CI and occasional local runs. This scans a small set of curated
content sources (hub JSON + hub page TSX + seed scripts) and validates any
https? URLs it finds.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx

URL_RE = re.compile(r"https?://[^\s\"'<>)}\\]]+")
TRAILING_PUNCTUATION_RE = re.compile(r"[),.;:!?]+$")


DEFAULT_SCAN_TARGETS = (
    "backend/data/hubs",
    "backend/scripts/seed_resources.py",
    "frontend/src/app/hubs",
)


DEFAULT_SKIP_PREFIXES = (
    "http://localhost",
    "https://localhost",
    "http://127.0.0.1",
    "https://127.0.0.1",
    "http://0.0.0.0",
    "https://0.0.0.0",
)


@dataclass(frozen=True)
class LinkCheckResult:
    url: str
    ok: bool
    status_code: int | None
    final_url: str | None
    error: str | None


def _repo_root() -> Path:
    # backend/scripts/check_links.py -> repo root is two parents up
    return Path(__file__).resolve().parents[2]


def _iter_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if not target.exists():
        return []

    exts = {".json", ".py", ".tsx", ".ts", ".md"}
    return [p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in exts]


def _normalize_url(url: str) -> str:
    url = url.strip()
    url = TRAILING_PUNCTUATION_RE.sub("", url)
    return url


def _extract_urls_from_json_value(value: object) -> set[str]:
    urls: set[str] = set()
    if isinstance(value, dict):
        for v in value.values():
            urls |= _extract_urls_from_json_value(v)
    elif isinstance(value, list):
        for v in value:
            urls |= _extract_urls_from_json_value(v)
    elif isinstance(value, str):
        for match in URL_RE.findall(value):
            urls.add(_normalize_url(match))
    return urls


def extract_urls(path: Path) -> set[str]:
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # Fall back to regex scanning if JSON isn't valid.
            return {_normalize_url(m) for m in URL_RE.findall(path.read_text(encoding="utf-8"))}
        return _extract_urls_from_json_value(data)

    return {_normalize_url(m) for m in URL_RE.findall(path.read_text(encoding="utf-8"))}


def should_skip_url(url: str, skip_prefixes: tuple[str, ...]) -> bool:
    return url.startswith(skip_prefixes)


def is_hard_failure(status_code: int | None, error: str | None, *, strict: bool) -> bool:
    # Always treat 404/410 as failures (page removed / not found).
    if status_code in (404, 410):
        return True

    # In strict mode, treat network errors and 5xx as failures too.
    if strict:
        if error:
            return True
        if status_code is None:
            return True
        if 500 <= status_code <= 599:
            return True

    return False


async def check_one(
    client: httpx.AsyncClient,
    url: str,
    retries: int,
) -> LinkCheckResult:
    last_error: str | None = None
    for attempt in range(retries + 1):
        try:
            resp = await client.get(url)
            return LinkCheckResult(
                url=url,
                ok=resp.status_code < 400,
                status_code=resp.status_code,
                final_url=str(resp.url),
                error=None,
            )
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as e:
            last_error = str(e)
            if attempt < retries:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            return LinkCheckResult(
                url=url,
                ok=False,
                status_code=None,
                final_url=None,
                error=last_error,
            )
        except httpx.HTTPError as e:
            return LinkCheckResult(
                url=url,
                ok=False,
                status_code=None,
                final_url=None,
                error=str(e),
            )

    return LinkCheckResult(url=url, ok=False, status_code=None, final_url=None, error=last_error)


async def check_all(
    urls: list[str],
    timeout_seconds: float,
    max_concurrency: int,
    retries: int,
) -> list[LinkCheckResult]:
    semaphore = asyncio.Semaphore(max_concurrency)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Vibe4VetsLinkChecker/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(timeout_seconds),
        headers=headers,
    ) as client:

        async def _guarded(url: str) -> LinkCheckResult:
            async with semaphore:
                return await check_one(client, url, retries=retries)

        return await asyncio.gather(*(_guarded(u) for u in urls))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check curated external links for breakage.")
    parser.add_argument(
        "--targets",
        nargs="*",
        default=list(DEFAULT_SCAN_TARGETS),
        help="Files/directories (relative to repo root) to scan for URLs.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=12,
        help="Maximum concurrent requests.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=1,
        help="Retries for transient connection/timeout errors.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also fail on network errors and 5xx responses (may be flaky).",
    )
    args = parser.parse_args(argv)

    root = _repo_root()
    files: list[Path] = []
    for t in args.targets:
        files.extend(_iter_files(root / t))

    urls: set[str] = set()
    for f in files:
        urls |= extract_urls(f)

    urls = {u for u in urls if not should_skip_url(u, DEFAULT_SKIP_PREFIXES)}

    if not urls:
        print("No URLs found.")
        return 0

    url_list = sorted(urls)
    print(f"Checking {len(url_list)} URL(s)...")

    results = asyncio.run(
        check_all(
            url_list,
            timeout_seconds=args.timeout,
            max_concurrency=args.max_concurrency,
            retries=args.retries,
        )
    )

    failures: list[LinkCheckResult] = []
    warnings: list[LinkCheckResult] = []

    for r in results:
        if is_hard_failure(r.status_code, r.error, strict=bool(args.strict)):
            failures.append(r)
        elif not r.ok:
            warnings.append(r)

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            status = f"HTTP {w.status_code}" if w.status_code is not None else "ERROR"
            final = f" -> {w.final_url}" if w.final_url and w.final_url != w.url else ""
            print(f"- {status}: {w.url}{final}")

    if failures:
        print(f"\nFailures ({len(failures)}):")
        for f in failures:
            status = f"HTTP {f.status_code}" if f.status_code is not None else "ERROR"
            detail = f" ({f.error})" if f.error else ""
            final = f" -> {f.final_url}" if f.final_url and f.final_url != f.url else ""
            print(f"- {status}: {f.url}{final}{detail}")
        return 1

    print("\nAll checked links look OK (within failure policy).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
