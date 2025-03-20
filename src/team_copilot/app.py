"""Team Copilot - API."""

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

import uvicorn

from team_copilot.core.db import check_db_status
from team_copilot.config import Settings, get_settings, settings


# HTTP status codes
HTTP_ISE_STATUS_CODE = 500  # Internal Server Error
HTTP_SU_STATUS_CODE = 503  # Service Unavailable

# Application status IDs
APP_OK_STATUS_ID = "ok"
APP_ERROR_STATUS_ID = "error"

# Names and messages
APP_WELCOME_MESSAGE = f"Welcome to {settings.app_name}!"
APP_OK_MESSAGE = "The application is running."
APP_ISE_MESSAGE = "Internal Server Error."

DB_OK_MESSAGE = "The database is available."
DB_ERROR_MESSAGE = "The database is not available."


# Application object
app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    version=settings.app_version,
)


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions.

    Args:
        request (Request): Request.
        exc (Exception): Exception.

    Returns:
        JSONResponse: JSON response.
    """
    return JSONResponse(
        {"status": APP_ERROR_STATUS_ID, "message": APP_ISE_MESSAGE},
        HTTP_ISE_STATUS_CODE,
    )


@app.get("/")
def index() -> JSONResponse:
    """Get a welcome message.

    Returns:
        JSONResponse: Welcome message.
    """
    return {"message": APP_WELCOME_MESSAGE}


@app.get("/health")
def health() -> JSONResponse:
    """Check the status of the application.

    Returns:
        JSONResponse: Application status.
    """
    return {"status": APP_OK_STATUS_ID, "message": APP_OK_MESSAGE}


@app.get("/health/db")
def db_health(settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Check the status of the database.

    Args:
        settings (Settings): Settings.

    Returns:
        JSONResponse: Database status.
    """
    if check_db_status(settings.db_url):
        return {"status": APP_OK_STATUS_ID, "message": DB_OK_MESSAGE}
    else:
        return JSONResponse(
            {"status": APP_ERROR_STATUS_ID, "message": DB_ERROR_MESSAGE},
            HTTP_SU_STATUS_CODE,
        )


def run(host: str, port: int):
    """Run the application.

    Args:
        host (str): Host.
        port (int): Port.
    """
    uvicorn.run(app, host=host, port=port)
