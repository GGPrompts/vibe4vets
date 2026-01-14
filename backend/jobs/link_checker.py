"""Link health checker job.

Validates resource URLs are still active and content is current.
Uses HTTP validation and Claude Haiku AI analysis to detect:
- Broken links (404, 500 errors)
- Redirects to different domains
- Pages that no longer contain relevant content
- "Not found" or "page removed" content
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
from sqlmodel import Session, select

from app.config import settings
from app.models.resource import Resource, ResourceStatus
from jobs.base import BaseJob

# HTTP client timeout settings
HTTP_TIMEOUT = 30.0  # seconds
MAX_REDIRECTS = 5

# Batch size for processing resources
BATCH_SIZE = 50

# AI validation threshold - below this score, flag for review
AI_HEALTH_THRESHOLD = 0.5


class LinkCheckerJob(BaseJob):
    """Job to validate resource URLs and flag broken/stale links.

    Uses a two-phase validation approach:
    1. HTTP validation: Check status codes, redirects, response times
    2. AI validation: Use Claude Haiku to analyze if content still represents
       an active veteran resource

    Resources with issues are flagged for human review.
    """

    @property
    def name(self) -> str:
        return "link_checker"

    @property
    def description(self) -> str:
        return "Validate resource URLs and flag broken/stale links"

    def execute(
        self,
        session: Session,
        resource_id: UUID | str | None = None,
        skip_ai: bool = False,
        batch_size: int = BATCH_SIZE,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run link health checks on resources.

        Args:
            session: Database session.
            resource_id: Optional specific resource to check.
                        If None, checks all resources with URLs.
            skip_ai: If True, skip AI validation (faster but less thorough).
            batch_size: Number of resources to process per batch.
            **kwargs: Additional arguments (ignored).

        Returns:
            Statistics dictionary with counts.
        """
        # Get resources to check
        resources = self._get_resources(session, resource_id, batch_size)

        if not resources:
            return {
                "checked": 0,
                "healthy": 0,
                "broken": 0,
                "flagged": 0,
                "skipped": 0,
                "message": "No resources with URLs to check",
            }

        self._log(f"Checking {len(resources)} resource(s)")

        stats = {
            "checked": 0,
            "healthy": 0,
            "broken": 0,
            "flagged": 0,
            "skipped": 0,
            "errors": [],
        }

        # Create HTTP client
        with httpx.Client(
            timeout=HTTP_TIMEOUT,
            follow_redirects=True,
            max_redirects=MAX_REDIRECTS,
        ) as client:
            for resource in resources:
                try:
                    result = self._check_resource(
                        client=client,
                        session=session,
                        resource=resource,
                        skip_ai=skip_ai,
                    )
                    stats["checked"] += 1

                    if result["status"] == "healthy":
                        stats["healthy"] += 1
                    elif result["status"] == "broken":
                        stats["broken"] += 1
                    elif result["status"] == "flagged":
                        stats["flagged"] += 1

                except Exception as e:
                    stats["skipped"] += 1
                    stats["errors"].append({
                        "resource_id": str(resource.id),
                        "error": str(e),
                    })
                    self._log(
                        f"Error checking resource {resource.id}: {e}",
                        level="warning",
                    )

        # Commit all changes
        session.commit()

        return stats

    def _get_resources(
        self,
        session: Session,
        resource_id: UUID | str | None,
        batch_size: int,
    ) -> list[Resource]:
        """Get resources to check.

        Args:
            session: Database session.
            resource_id: Specific resource ID or None for batch.
            batch_size: Maximum number to return.

        Returns:
            List of resources with URLs to check.
        """
        if resource_id:
            # Check specific resource
            if isinstance(resource_id, str):
                resource_id = UUID(resource_id)

            stmt = select(Resource).where(Resource.id == resource_id)
            resource = session.exec(stmt).first()
            return [resource] if resource and resource.website else []

        # Get batch of resources with URLs, prioritizing those not recently checked
        stmt = (
            select(Resource)
            .where(Resource.website.isnot(None))  # type: ignore[union-attr]
            .where(Resource.status == ResourceStatus.ACTIVE)
            .order_by(Resource.link_checked_at.asc().nullsfirst())  # type: ignore[union-attr]
            .limit(batch_size)
        )
        return list(session.exec(stmt).all())

    def _check_resource(
        self,
        client: httpx.Client,
        session: Session,
        resource: Resource,
        skip_ai: bool,
    ) -> dict[str, Any]:
        """Check a single resource's URL health.

        Args:
            client: HTTP client instance.
            session: Database session.
            resource: Resource to check.
            skip_ai: Whether to skip AI validation.

        Returns:
            Result dictionary with status and details.
        """
        url = resource.website
        if not url:
            return {"status": "skipped", "reason": "no_url"}

        # Ensure URL has scheme
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        self._log(f"Checking: {url}")

        # Phase 1: HTTP validation
        http_result = self._http_check(client, url)

        # Update resource with HTTP results
        resource.link_checked_at = datetime.now(UTC)
        resource.link_http_status = http_result["status_code"]

        # Check for broken link
        if http_result["status_code"] and http_result["status_code"] >= 400:
            resource.link_health_score = 0.0
            resource.link_flagged_reason = f"HTTP {http_result['status_code']}"
            resource.status = ResourceStatus.NEEDS_REVIEW
            session.add(resource)
            return {"status": "broken", "http_status": http_result["status_code"]}

        # Check for errors (connection failed, timeout, etc.)
        if http_result.get("error"):
            resource.link_health_score = 0.0
            resource.link_flagged_reason = http_result["error"]
            resource.status = ResourceStatus.NEEDS_REVIEW
            session.add(resource)
            return {"status": "broken", "error": http_result["error"]}

        # Phase 2: AI validation (if enabled and we have content)
        ai_score = 1.0  # Default to healthy
        if not skip_ai and http_result.get("content") and settings.anthropic_api_key:
            ai_result = self._ai_validate(
                url=url,
                content=http_result["content"],
                resource_title=resource.title,
            )
            ai_score = ai_result.get("score", 1.0)

            if ai_score < AI_HEALTH_THRESHOLD:
                resource.link_flagged_reason = ai_result.get(
                    "reason", "AI flagged as potentially inactive"
                )
                resource.status = ResourceStatus.NEEDS_REVIEW

        # Update health score
        resource.link_health_score = ai_score
        session.add(resource)

        if ai_score < AI_HEALTH_THRESHOLD:
            return {"status": "flagged", "ai_score": ai_score}

        # Clear any previous flags if now healthy
        if resource.link_flagged_reason:
            resource.link_flagged_reason = None

        return {"status": "healthy", "ai_score": ai_score}

    def _http_check(self, client: httpx.Client, url: str) -> dict[str, Any]:
        """Perform HTTP check on a URL.

        Args:
            client: HTTP client instance.
            url: URL to check.

        Returns:
            Dictionary with status_code, content, error, etc.
        """
        try:
            response = client.get(url)

            # Extract relevant content for AI analysis (truncate to save tokens)
            content = response.text[:5000] if response.text else ""

            return {
                "status_code": response.status_code,
                "content": content,
                "final_url": str(response.url),
                "redirected": str(response.url) != url,
            }

        except httpx.TimeoutException:
            return {"status_code": None, "error": "timeout"}
        except httpx.TooManyRedirects:
            return {"status_code": None, "error": "too_many_redirects"}
        except httpx.ConnectError as e:
            return {"status_code": None, "error": f"connection_failed: {e}"}
        except httpx.HTTPError as e:
            return {"status_code": None, "error": f"http_error: {e}"}

    def _ai_validate(
        self,
        url: str,
        content: str,
        resource_title: str,
    ) -> dict[str, Any]:
        """Use Claude Haiku to validate if the page is still an active resource.

        Args:
            url: The URL being checked.
            content: Page content (HTML/text).
            resource_title: The resource title for context.

        Returns:
            Dictionary with score (0-1) and optional reason.
        """
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

            prompt = f"""
Analyze this web page content to determine if it represents an active veteran resource.

Resource Title: {resource_title}
URL: {url}

Page Content (first 5000 chars):
{content}

Evaluate:
1. Does the page still exist (not a 404 page, parked domain, or error page)?
2. Does it contain information about veteran services/resources?
3. Does it appear to be actively maintained (not abandoned)?
4. Are there signs of current contact info, dates, or active programs?

Respond in this exact format:
SCORE: [0.0-1.0 where 1.0 is definitely active, 0.0 is definitely inactive]
REASON: [Brief explanation if score < 0.7]

Examples:
- Active resource page with current info: SCORE: 0.95
- Page exists but outdated/unmaintained: SCORE: 0.6
- 404 or error page: SCORE: 0.1
- Parked domain or unrelated content: SCORE: 0.2
""".strip()

            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            response_text = message.content[0].text
            lines = response_text.strip().split("\n")

            score = 1.0
            reason = None

            for line in lines:
                if line.startswith("SCORE:"):
                    try:
                        score = float(line.replace("SCORE:", "").strip())
                        score = max(0.0, min(1.0, score))  # Clamp to 0-1
                    except ValueError:
                        pass
                elif line.startswith("REASON:"):
                    reason = line.replace("REASON:", "").strip()

            return {"score": score, "reason": reason}

        except Exception as e:
            self._log(f"AI validation failed: {e}", level="warning")
            # Default to healthy if AI validation fails
            return {"score": 1.0, "reason": None}

    def _format_message(self, stats: dict[str, Any]) -> str:
        """Format check statistics into a message."""
        checked = stats.get("checked", 0)
        healthy = stats.get("healthy", 0)
        broken = stats.get("broken", 0)
        flagged = stats.get("flagged", 0)

        return (
            f"Link check complete: {checked} checked, "
            f"{healthy} healthy, {broken} broken, {flagged} flagged"
        )
