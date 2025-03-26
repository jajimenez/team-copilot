"""Team Copilot - Core - Security."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext

from team_copilot.db.session import get_session
from team_copilot.models.models import TokenData, User, DbUser
from team_copilot.core.config import settings


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
