"""Team Copilot - Main."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session

from team_copilot.db.setup import setup
from team_copilot.db.status import check_status
from team_copilot.db.session import get_session
from team_copilot.core.config import Settings, get_settings, settings


# HTTP status codes
HTTP_ISE_STATUS_CODE = 500  # Internal Server Error
HTTP_SU_STATUS_CODE = 503  # Service Unavailable

# Names and messages
APP_WELCOME_MESSAGE = f"Welcome to {settings.app_name}!"
APP_OK_MESSAGE = "The application is running."
APP_ISE_MESSAGE = "Internal server error."

DB_OK_MESSAGE = "The database is available."
DB_ERROR_MESSAGE = "The database is not available."

# Dependencies
SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan.

    Args:
        app (FastAPI): FastAPI application
    """
    # Set up the database on startup
    setup(settings.db_url)
    yield
    # Any logic to run on shutdown would go here


# Application object
app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception):
    """Handle exceptions.

    Args:
        request (Request): Request.
        exc (Exception): Exception.
    """
    return JSONResponse(
        status_code=HTTP_ISE_STATUS_CODE,
        content={"detail": APP_ISE_MESSAGE},
    )


@app.get("/")
def index():
    """Get a welcome message."""
    return {"detail": APP_WELCOME_MESSAGE}


@app.get("/health")
def health():
    """Check the status of the application."""
    return {"detail": APP_OK_MESSAGE}


@app.get("/health/db")
def db_health(settings: Settings = Depends(get_settings)):
    """Check the status of the database.

    Args:
        settings (Settings): Settings.
    """
    if check_status(settings.db_url):
        return {"detail": DB_OK_MESSAGE}

    raise HTTPException(status_code=HTTP_SU_STATUS_CODE, detail=DB_ERROR_MESSAGE)
