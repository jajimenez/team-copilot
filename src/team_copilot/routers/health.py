"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Response, Depends, status

from team_copilot.core.config import Settings, get_settings
from team_copilot.db.status import check_status
from team_copilot.models.data import AppStatus, DbStatus
from team_copilot.models.response import AppStatusResponse, DbStatusResponse


# Descriptions and messages
APP_AVA_1 = "Application is available"
APP_AVA_2 = "Application is available."
DB_AVA_1 = "Database is available"
DB_AVA_2 = "Database is available."
DB_UNA_1 = "Database is unavailable"
DB_UNA_2 = "Database is unavailable."
GET_APP_STATUS_DESC = "Get the application status."
GET_APP_STATUS_SUM = "Get the application status"
GET_DB_STATUS_DESC = "Get the database status."
GET_DB_STATUS_SUM = "Get the database status"

# Examples
DB_AVA_EX = DbStatusResponse.create(message=DB_AVA_2, status=DbStatus.AVAILABLE)
DB_AVA_EX = DB_AVA_EX.model_dump()

DB_UNA_EX = DbStatusResponse.create(message=DB_UNA_2, status=DbStatus.UNAVAILABLE)
DB_UNA_EX = DB_UNA_EX.model_dump()

# Router
router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/app",
    operation_id="get_app_status",
    summary=GET_APP_STATUS_SUM,
    description=GET_APP_STATUS_DESC,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": APP_AVA_1,
            "model": AppStatusResponse,
        }
    },
)
async def get_app_status() -> AppStatusResponse:
    """Get the status of the application.

    Returns:
        AppStatusResponse: Message and application status.
    """
    return AppStatusResponse.create(message=APP_AVA_2, status=AppStatus.AVAILABLE)


@router.get(
    "/db",
    operation_id="get_db_status",
    summary=GET_DB_STATUS_SUM,
    description=GET_DB_STATUS_DESC,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": DB_AVA_1,
            "model": DbStatusResponse,
            "content": {"application/json": {"example": DB_AVA_EX}},
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": DB_UNA_1,
            "model": DbStatusResponse,
            "content": {"application/json": {"example": DB_UNA_EX}},
        },
    },
)
async def get_db_status(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> DbStatusResponse:
    """Check the status of the database.

    Args:
        response (Response): Response object.
        settings (Settings): Application settings.

    Returns:
        DbStatusResponse: Message and database status.
    """
    if check_status(settings.db_url):
        return DbStatusResponse.create(message=DB_AVA_2, status=DbStatus.AVAILABLE)

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return DbStatusResponse.create(message=DB_UNA_2, status=DbStatus.UNAVAILABLE)
