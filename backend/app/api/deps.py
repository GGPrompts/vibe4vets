"""FastAPI dependencies for authentication and authorization."""

import hashlib
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from app.config import settings


class AdminAuth:
    """Dependency for admin API key authentication.

    Validates the X-Admin-Key header against a SHA-256 hash stored in
    the ADMIN_API_KEY_HASH environment variable.
    """

    def __init__(self) -> None:
        self.api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

    def __call__(
        self,
        api_key: Annotated[str | None, Depends(APIKeyHeader(name="X-Admin-Key", auto_error=False))] = None,
    ) -> None:
        """Validate the admin API key.

        Raises:
            HTTPException: 401 if key is missing or invalid, 503 if auth not configured
        """
        # Check if admin auth is configured
        if not settings.admin_api_key_hash:
            raise HTTPException(
                status_code=503,
                detail="Admin authentication not configured. Set ADMIN_API_KEY_HASH.",
            )

        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="Missing API key. Include X-Admin-Key header.",
            )

        # Hash the provided key and compare
        provided_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if provided_hash != settings.admin_api_key_hash:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key.",
            )


# Reusable dependency type
AdminAuthDep = Annotated[None, Depends(AdminAuth())]
