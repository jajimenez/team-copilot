"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Response, Depends, status

from team_copilot.db.status import check_status
from team_copilot.models.models import AppStatusResponse, DbStatus, DbStatusResponse
from team_copilot.core.config import Settings, get_settings


APP_AVAILABLE = "Application is available."
DB_AVAILABLE = "Database is available."
DB_UNAVAILABLE = "Database is unavailable."

# Router
router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/app",
    responses={status.HTTP_200_OK: {"description": APP_AVAILABLE}},
    response_model=AppStatusResponse,
)
def get_app_status() -> AppStatusResponse:
    """Check the status of the application.

    Returns:
        AppStatusResponse: Application status response.
    """
    return AppStatusResponse()


@router.get(
    "/db",
    responses={
        status.HTTP_200_OK: {"description": DB_AVAILABLE},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": DB_UNAVAILABLE},
    },
    response_model=DbStatusResponse,
)
def get_db_status(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> DbStatusResponse:
    """Check the status of the database.

    Args:
        response (Response): Response object.
        settings (Settings): Application settings.

    Returns:
        DbStatusResponse: Database status response.
    """
    if check_status(settings.db_url):
        return DbStatusResponse(status=DbStatus.AVAILABLE)

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return DbStatusResponse(status=DbStatus.UNAVAILABLE)
