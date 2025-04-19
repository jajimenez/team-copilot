"""Team Copilot - Main."""

from contextlib import asynccontextmanager

# from typing import Annotated

# from fastapi import FastAPI, Depends, Request, status
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException

# from sqlmodel import Session

from team_copilot.db.setup import setup
from team_copilot.routers import health, auth, users, documents

# from team_copilot.db.session import get_session
from team_copilot.models.response import MessageResponse
from team_copilot.core.config import settings


# Messages
INTERNAL_SERVER_ERROR = "Internal server error"

APP_WELCOME = f"Welcome to {settings.app_name}!"
APP_OK = "The application is running."
APP_ISE = "Internal server error."
APP_INV_CRED = "Invalid credentials"

DB_OK = "The database is available."
DB_ERROR_MESSAGE = "The database is not available."

# API documentation
ROOT_DESC = "Get a welcome message."

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
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": INTERNAL_SERVER_ERROR,
            "model": MessageResponse,
        },
    }
)

# Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)


@app.exception_handler(RequestValidationError)
async def handle_reqval_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle RequestValidationError exceptions.

    Args:
        request (Request): Request.
        exc (RequestValidationError): Exception.
    
    Returns:
        JSONResponse: Error message.
    """
    msg = [i["msg"] for i in exc.errors()]
    msg = ", ".join(msg)

    msg_res = MessageResponse(message=msg)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=msg_res.model_dump(),
    )


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException exceptions.

    Args:
        request (Request): Request.
        exc (HTTPException): Exception.

    Returns:
        JSONResponse: Error message.
    """
    msg_res = MessageResponse(message=exc.detail)
    return JSONResponse(status_code=exc.status_code, content=msg_res.model_dump())


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle Exception exceptions.

    Args:
        request (Request): Request.
        exc (Exception): Exception.

    Returns:
        JSONResponse: Error message.
    """
    msg_res = MessageResponse(message=APP_ISE)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=msg_res.model_dump(),
    )


@app.get("/", description=ROOT_DESC, response_model=MessageResponse)
def index() -> MessageResponse:
    """Get a welcome message.

    Returns:
        MessageResponse: Welcome message.
    """
    return MessageResponse(message=APP_WELCOME)
