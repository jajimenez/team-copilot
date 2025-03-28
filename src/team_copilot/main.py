"""Team Copilot - Main."""

from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import Session

from team_copilot.db.setup import setup
from team_copilot.db.status import check_status
from team_copilot.db.session import get_session
from team_copilot.models.models import Message, Token, User
from team_copilot.core.config import Settings, get_settings, settings

from team_copilot.core.security import (
    authenticate_user,
    create_access_token,
    get_current_act_user,
)


# Messages
APP_WELCOME = f"Welcome to {settings.app_name}!"
APP_OK = "The application is running."
APP_ISE = "Internal server error."
APP_INV_CRED = "Invalid credentials"

DB_OK = "The database is available."
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
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": APP_ISE},
    )


@app.get("/")
def index() -> Message:
    """Get a welcome message.

    Returns:
        Message: Welcome message.
    """
    return Message(detail=APP_WELCOME)


@app.get("/health")
def get_status() -> Message:
    """Check the status of the application.

    Returns:
        Message: Status message.
    """
    return Message(detail=APP_OK)


@app.get("/health/db")
def get_db_status(settings: Annotated[Settings, Depends(get_settings)]) -> Message:
    """Check the status of the database.

    Args:
        settings (Settings): Application settings.

    Returns:
        Message: Status message.
    """
    if check_status(settings.db_url):
        return Message(detail=DB_OK)

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=DB_ERROR_MESSAGE,
    )


@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Get an authentication token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data.

    Returns:
        Token: Token.
    """
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        headers = {"WWW-Authenticate": "Bearer"}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers=headers,
        )

    exp = timedelta(minutes=settings.app_acc_token_exp_min)
    token = create_access_token(data={"sub": user.username}, exp_delta=exp)

    return Token(access_token=token, token_type="bearer")


@app.get("/me")
def get_current_user(
    current_user: Annotated[User, Depends(get_current_act_user)],
) -> User:
    """Get the current user.

    Args:
        current_user (User): Current user.

    Returns:
        User: Current user.
    """
    return current_user
