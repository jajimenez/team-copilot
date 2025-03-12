"""Team Copilot - API."""

from os import getenv

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from team_copilot import __version__ as version
from team_copilot.db import check_status


HTTP_ISE_STATUS_CODE = 500  # Internal Server Error
HTTP_SU_STATUS_CODE = 503  # Service Unavailable

OK_STATUS_ID = "ok"
ERROR_STATUS_ID = "error"

API_NAME = "Team Copilot"
API_WELCOME_MESSAGE = f"Welcome to {API_NAME}!"
API_OK_STATUS_MESSAGE = "The API is running."
API_ISE_MESSAGE = "Internal Server Error."
DB_OK_STATUS_MESSAGE = "The database is available."
DB_ERROR_STATUS_MESSAGE = "The database is not available."

DEBUG = getenv("TEAM_COPILOT_DEBUG", "false").lower() == "true"

app = FastAPI(debug=DEBUG, title=API_NAME, version=version)


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception):
    """Handle exceptions.

    Args:
        request (Request): Request.
        exc (Exception): Exception.

    Returns:
        JSONResponse: JSON response.
    """
    return JSONResponse(
        {"status": ERROR_STATUS_ID, "message": API_ISE_MESSAGE},
        HTTP_ISE_STATUS_CODE,
    )


@app.get("/")
def index():
    return {"message": API_WELCOME_MESSAGE}


@app.get("/health")
def health():
    """Check the status of the API."""
    return {"status": OK_STATUS_ID, "message": API_OK_STATUS_MESSAGE}


@app.get("/health/db")
def db_health():
    """Check the status of the database."""
    if check_status():
        return {"status": OK_STATUS_ID, "message": DB_OK_STATUS_MESSAGE}
    else:
        return JSONResponse(
            {"status": ERROR_STATUS_ID, "message": DB_ERROR_STATUS_MESSAGE},
            HTTP_SU_STATUS_CODE,
        )


def run(host: str = "127.0.0.1", port: int = 8000):
    """Run the API.

    Args:
        host (str): Host (default: 127.0.0.1).
        port (int): Port (default: 8000).
    """
    # Run the API
    uvicorn.run(app, host=host, port=port)
