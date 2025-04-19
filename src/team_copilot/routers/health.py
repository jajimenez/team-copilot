"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Response, Depends, status

from team_copilot.core.config import Settings, get_settings
from team_copilot.db.status import check_status
from team_copilot.models.data import DbStatus
from team_copilot.models.response import AppStatusResponse, DbStatusResponse


# Descriptions
GET_APP_STATUS_DESC = "Get the status of the application."
GET_DB_STATUS_DESC = "Get the status of the database."

# Messages
APP_AVAILABLE = "Application is available."
DB_AVAILABLE = "Database is available."
DB_UNAVAILABLE = "Database is unavailable."

# Examples
DB_AVAILABLE_EX = DbStatusResponse(status=DbStatus.AVAILABLE).model_dump()
DB_UNAVAILABLE_EX = DbStatusResponse(status=DbStatus.UNAVAILABLE).model_dump()

# Router
router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/app",
    description=GET_APP_STATUS_DESC,
    responses={status.HTTP_200_OK: {"description": APP_AVAILABLE}},
    response_model=AppStatusResponse,
)
def get_app_status() -> AppStatusResponse:
    """Get the status of the application.

    Returns:
        AppStatusResponse: Application status response.
    """
    return AppStatusResponse()


@router.get(
    "/db",
    description=GET_DB_STATUS_DESC,
    responses={
        status.HTTP_200_OK: {
            "description": DB_AVAILABLE,
            "model": DbStatusResponse,
            "content": {"application/json": {"example": DB_AVAILABLE_EX}},
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": DB_UNAVAILABLE,
            "model": DbStatusResponse,
            "content": {"application/json": {"example": DB_UNAVAILABLE_EX}},
        },
    },
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
