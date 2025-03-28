"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from team_copilot.db.status import check_status
from team_copilot.models.models import Message
from team_copilot.core.config import Settings, get_settings


# Messages
APP_OK = "The application is running."

DB_OK = "The database is available."
DB_ERROR_MESSAGE = "The database is not available."

# Router
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/app")
def get_app_status() -> Message:
    """Check the status of the application.

    Returns:
        Message: Status message.
    """
    return Message(detail=APP_OK)


@router.get(
    "/db",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Service Unavailable"}
    },
)
def get_db_status(settings: Annotated[Settings, Depends(get_settings)]) -> Message:
    """Check the status of the database.

    Args:
        settings (Settings): Application settings.

    Returns:
        Message: Status message.
    """
    if check_status(settings.db_url):
        return Message(detail=DB_OK)

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=DB_ERROR_MESSAGE,
    )
