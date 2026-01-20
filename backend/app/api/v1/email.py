"""Email endpoints for sending resource lists to users."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr

from app.database import SessionDep
from app.services.email import send_resources_email
from app.services.resource import ResourceService

router = APIRouter()


class EmailResourcesRequest(BaseModel):
    """Request body for emailing resources."""

    email: EmailStr
    resource_ids: list[str]


class EmailResourcesResponse(BaseModel):
    """Response for email endpoint."""

    success: bool
    message: str


@router.post(
    "",
    response_model=EmailResourcesResponse,
    summary="Email resources to user",
    response_description="Confirmation of email being queued",
    responses={
        200: {
            "description": "Email queued successfully",
            "content": {
                "application/json": {"example": {"success": True, "message": "Email sent to user@example.com"}}
            },
        },
        400: {
            "description": "Invalid request",
            "content": {"application/json": {"example": {"detail": "No resources found with the provided IDs"}}},
        },
    },
)
def email_resources(
    request: EmailResourcesRequest,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> EmailResourcesResponse:
    """Send a formatted list of resources to the specified email address.

    This endpoint accepts a list of resource IDs and sends a formatted email
    containing the resource details to the provided email address.

    The email is sent in the background to avoid blocking the request.

    **Request Body:**
    - `email` - Valid email address to send the resources to
    - `resource_ids` - List of resource UUIDs to include in the email

    **Returns:**
    - Confirmation that the email has been queued for delivery
    """
    if not request.resource_ids:
        raise HTTPException(status_code=400, detail="No resource IDs provided")

    # Fetch the resources
    service = ResourceService(session)
    resources = []

    for rid in request.resource_ids:
        try:
            resource = service.get_resource(UUID(rid))
            if resource:
                resources.append(resource)
        except (ValueError, TypeError):
            # Skip invalid UUIDs
            pass

    if not resources:
        raise HTTPException(status_code=400, detail="No valid resources found with the provided IDs")

    # Queue email in background
    background_tasks.add_task(send_resources_email, request.email, resources)

    return EmailResourcesResponse(
        success=True,
        message=f"Email queued for delivery to {request.email}",
    )
