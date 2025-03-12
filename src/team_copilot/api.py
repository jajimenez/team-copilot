"""Team Copilot - API."""

from os import getenv

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from team_copilot import __version__ as version
from team_copilot.db import check_status


HTTP_SERVICE_UNAVAILABLE_STATUS_CODE = 503

OK_STATUS_ID = "ok"
ERROR_STATUS_ID = "error"

API_NAME = "Team Copilot"
API_WELCOME_MESSAGE = f"Welcome to {API_NAME}!"
API_OK_STATUS_MESSAGE = "The API is running."
DB_OK_STATUS_MESSAGE = "The database is available."
DB_ERROR_STATUS_MESSAGE = "The database is not available."

DEBUG = getenv("TEAM_COPILOT_DEBUG", "false").lower() == "true"

app = FastAPI(debug=DEBUG, title=API_NAME, version=version)


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
            HTTP_SERVICE_UNAVAILABLE_STATUS_CODE,
        )


def run(host: str = "127.0.0.1", port: int = 8000):
    """Run the API.

    Args:
        host (str): Host (default: 127.0.0.1).
        port (int): Port (default: 8000).
    """
    # Run the API
    uvicorn.run(app, host=host, port=port)
