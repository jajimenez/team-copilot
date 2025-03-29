"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from team_copilot.db.status import check_status
from team_copilot.models.models import Message
from team_copilot.core.config import Settings, get_settings


# Messages
APP_RUNNING = "Application running"

DB_AVAILABLE = "Database available"
DB_NOT_AVAILABLE = "Database not available"

# Router
router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/app",
    responses={status.HTTP_200_OK: {"description": APP_RUNNING}},
    response_model=Message
)
def get_app_status() -> Message:
    """Check the status of the application.

    Returns:
        Message: Status message.
    """
    return Message(detail=APP_RUNNING)


@router.get(
    "/db",
    responses={
        status.HTTP_200_OK: {"description": DB_AVAILABLE},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": DB_NOT_AVAILABLE}
    },
    response_model=Message,
)
def get_db_status(settings: Annotated[Settings, Depends(get_settings)]) -> Message:
    """Check the status of the database.

    Args:
        settings (Settings): Application settings.

    Raises:
        HTTPException: If the database is not available.

    Returns:
        Message: Status message.
    """
    if check_status(settings.db_url):
        return Message(detail=DB_AVAILABLE)

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=DB_NOT_AVAILABLE,
    )
