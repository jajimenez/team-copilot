"""Team Copilot - Main."""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlmodel import Session

import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext

from team_copilot.db.setup import setup
from team_copilot.db.status import check_status
from team_copilot.db.session import get_session
from team_copilot.models.models import Message, Token, TokenData, User, DbUser
from team_copilot.core.config import Settings, get_settings, settings


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

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(username: str) -> DbUser | None:
    """Get a user by its username.

    Args:
        username (str): Username.

    Returns:
        DbUser | None: User if found, None otherwise.
    """
    with get_session() as session:
        user = session.exec(
            session.query(DbUser).filter(DbUser.username == username).first
        )

    return user


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password by comparing it to its hash.

    Args:
        password (str): Password.
        password_hash (str): Password hash.

    Returns:
        bool: Whether the password is correct.
    """
    return pwd_context.verify(password, password_hash)


def get_password_hash(password: str) -> str:
    """Get the hash of a password.

    Args:
        password (str): Password.

    Returns:
        str: Password hash.
    """
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> DbUser | None:
    """Authenticate a user by its username and password.

    Args:
        username (str): Username.
        password (str): Password.

    Returns:
        DbUser | None: User if authenticated, None otherwise.
    """
    user = get_user(username)

    # Check if the user exists, is enabled, and the password is correct.
    if (
        not user
        or not user.enabled
        or not verify_password(password, user.password_hash)
    ):
        return None

    return user


def create_access_token(data: dict, exp_delta: timedelta | None = None) -> str:
    """Create an access token.

    Args:
        data (dict): Data.
        exp_delta (timedelta | None): Expiration delta.

    Returns:
        str: Access token.
    """
    data = data.copy()

    if exp_delta:
        exp = datetime.now(timezone.utc) + exp_delta
    else:
        exp = datetime.now(timezone.utc) + timedelta(
            minutes=settings.app_acc_token_exp_min
        )

    data.update({"exp": exp})

    # Return the encoded token
    return jwt.encode(
        data, settings.app_secret_key, algorithm=settings.app_hash_algorithm
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get current user."""
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        data = jwt.decode(
            token,
            settings.app_secret_key,
            algorithms=[settings.app_hash_algorithm],
        )

        username: str = data.get("sub")

        if username is None:
            raise cred_exc

        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise cred_exc

    user = get_user(username=token_data.username)

    if user is None:
        raise cred_exc

    return user


async def get_current_act_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get current active user."""
    if not current_user.enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return current_user


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
