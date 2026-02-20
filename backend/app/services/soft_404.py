"""Soft 404 detection for resource URL validation.

Detects pages that return HTTP 200 but actually show error/not-found content.
Works without any LLM dependency - pure pattern matching on response content and URL behavior.
"""

import re
from urllib.parse import urlparse

# Phrases commonly found on soft 404 pages (checked against lowercased content)
SOFT_404_PHRASES = [
    "page not found",
    "page cannot be found",
    "page you requested",
    "no longer available",
    "no longer exists",
    "has been removed",
    "has been moved",
    "this page has moved",
    "this page does not exist",
    "404 error",
    "404 not found",
    "error 404",
    "we're sorry",
    "we couldn't find",
    "we could not find",
    "the resource you are looking for",
    "this program has ended",
    "this program is no longer",
    "requested url was not found",
    "nothing was found at this location",
    "doesn't exist or is no longer available",
]

# Patterns for <title> tag content (case-insensitive)
TITLE_404_PATTERNS = re.compile(
    r"(not\s*found|error\s*404|404\s*error|page\s*removed|page\s*not\s*found)",
    re.IGNORECASE,
)

# Minimum content length (chars) - pages shorter than this are suspicious
MIN_CONTENT_LENGTH = 500

# Short homepage paths that indicate redirect-to-homepage
HOMEPAGE_PATHS = {"", "/", "/en", "/en/", "/home", "/home/", "/index.html", "/index.htm"}


def detect_soft_404(
    content: str,
    original_url: str,
    final_url: str | None = None,
    title: str | None = None,
) -> dict:
    """Detect soft 404s from page content and URL behavior.

    Args:
        content: Page content (HTML or markdown text).
        original_url: The URL that was originally requested.
        final_url: The URL after redirects (if different from original).
        title: Page title (from <title> tag or metadata).

    Returns:
        {"is_soft_404": bool, "reason": str | None, "score": float}
        score is 0.1 for detected soft 404s, 1.0 for clean pages.
    """
    reasons = []
    content_lower = content.lower() if content else ""

    # Signal 1: Content keyword matching
    for phrase in SOFT_404_PHRASES:
        if phrase in content_lower:
            reasons.append(f"Content contains '{phrase}'")
            break  # One match is enough

    # Signal 2: Redirect to homepage detection
    if final_url and original_url:
        original_path = urlparse(original_url).path.rstrip("/")
        final_path = urlparse(final_url).path

        if (
            original_path
            and len(original_path) > 1
            and final_path.rstrip("/").lower() in {p.rstrip("/") for p in HOMEPAGE_PATHS}
        ):
            reasons.append(f"Redirected to homepage ({final_url})")

    # Signal 3: Suspiciously short content
    if content and 0 < len(content) < MIN_CONTENT_LENGTH:
        reasons.append(f"Very short content ({len(content)} chars)")

    # Signal 4: Title mismatch
    if title and TITLE_404_PATTERNS.search(title):
        reasons.append(f"Title suggests error page: '{title[:80]}'")

    if reasons:
        return {
            "is_soft_404": True,
            "reason": "; ".join(reasons),
            "score": 0.1,
        }

    return {
        "is_soft_404": False,
        "reason": None,
        "score": 1.0,
    }
