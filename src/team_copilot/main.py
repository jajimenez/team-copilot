"""Team Copilot - Main."""

from contextlib import asynccontextmanager

# from typing import Annotated

# from fastapi import FastAPI, Depends, Request, status
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

# from sqlmodel import Session

from team_copilot.db.setup import setup
from team_copilot.routers import health, auth, users, documents

# from team_copilot.db.session import get_session
from team_copilot.models.response import MessageResponse
from team_copilot.core.config import settings


# Messages
APP_WELCOME = f"Welcome to {settings.app_name}!"
APP_OK = "The application is running."
APP_ISE = "Internal server error."
APP_INV_CRED = "Invalid credentials"

DB_OK = "The database is available."
DB_ERROR_MESSAGE = "The database is not available."

# Dependencies
# SessionDep = Annotated[Session, Depends(get_session)]


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

# Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception):
    """Handle exceptions.

    Args:
        request (Request): Request.
        exc (Exception): Exception.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": APP_ISE},
    )


@app.get("/", response_model=MessageResponse)
def index() -> MessageResponse:
    """Get a welcome message.

    Returns:
        MessageResponse: Welcome message.
    """
    return MessageResponse(detail=APP_WELCOME)
