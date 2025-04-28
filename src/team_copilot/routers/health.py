"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Response, Depends, status

from team_copilot.core.config import Settings, get_settings
from team_copilot.db.status import check_status
from team_copilot.models.data import DbStatus
from team_copilot.models.response import AppStatusResponse, DbStatusResponse


# Descriptions and messages
APP_AVAILABLE = "Application is available."
DB_AVAILABLE = "Database is available."
DB_UNAVAILABLE = "Database is unavailable."
GET_APP_STATUS_DESC = "Get the application status."
GET_APP_STATUS_SUM = "Get the application status"
GET_DB_STATUS_DESC = "Get the database status."
GET_DB_STATUS_SUM = "Get the database status"

# Examples
DB_AVAILABLE_EX: dict = DbStatusResponse(status=DbStatus.AVAILABLE).model_dump()
DB_UNAVAILABLE_EX: dict = DbStatusResponse(status=DbStatus.UNAVAILABLE).model_dump()

# Router
router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/app",
    operation_id="get_app_status",
    summary=GET_APP_STATUS_SUM,
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
    operation_id="get_db_status",
    summary=GET_DB_STATUS_SUM,
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
