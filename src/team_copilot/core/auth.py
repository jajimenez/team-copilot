"""Team Copilot - Core - Authentication and Authorization."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from team_copilot.core.config import settings
from team_copilot.models.data import User
from team_copilot.services.users import get_user


# Messages
INV_CRED = "Invalid credentials."

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate a user by its username and password.

    Args:
        username (str): Username.
        password (str): Password.

    Returns:
        User | None: User if authentication is successful or None otherwise.
    """
    user = get_user(username=username)

    # Check that the user exists, it's enabled and the given password is correct.
    if not user or not user.enabled or not user.verify_password(password):
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


async def get_auth_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """Check if the current user is authenticated and return it if it is.

    This is a FastAPI dependency function that checks if the user is authenticated by
    verifying the access token. If the token is valid, it retrieves the user from the
    database. If the token is invalid or the user doesn't exist, it raises an exception.

    Args:
        token (str): Access token.

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.

    Returns:
        User: Current user (authenticated).
    """
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INV_CRED)

    try:
        data = jwt.decode(
            token,
            settings.app_secret_key,
            algorithms=[settings.app_hash_algorithm],
        )

        username: str = data.get("sub")

        if username is None:
            raise cred_exc
    except InvalidTokenError:
        raise cred_exc

    user = get_user(username=username)

    if not user:
        raise cred_exc

    return user


async def get_enabled_user(user: Annotated[User, Depends(get_auth_user)]) -> User:
    """Check if the current user is authenticated and enabled and return it if it is.

    This is a FastAPI dependency function that checks if the user is authenticated
    (through the "get_auth_user" dependency function) and enabled. If the user is not
    authenticated or is not enabled, it raises an exception.

    Args:
        user (User): Authenticated user.

    Raises:
        HTTPException: If the user is not authenticated or is not enabled.

    Returns:
        User: Current user (authenticated and enabled).
    """
    if not user.enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INV_CRED,
        )

    return user


async def get_staff_user(user: Annotated[User, Depends(get_enabled_user)]) -> User:
    """Check if the current user is authenticated, is enabled and is a staff member and
    return it if it is.

    This is a FastAPI dependency function that checks if the user is authenticated and
    enabled (through the "get_enabled_user" dependency function) and is a staff member.
    If the user is not authenticated, is not enabled or is not a staff member, it raises
    an exception.

    Args:
        user (User): Authenticated and enabled user.

    Raises:
        HTTPException: If the user is not authenticated, is not enabled or is not a
            staff member.

    Returns:
        User: Current user (authenticated and enabled and a staff member).
    """
    if not user.staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INV_CRED,
        )

    return user


async def get_admin_user(user: Annotated[User, Depends(get_enabled_user)]) -> User:
    """Check if the current user is authenticated, is enabled and is an administrator
    and return it if it is.

    This is a FastAPI dependency function that checks if the user is authenticated and
    enabled (through the "get_enabled_user" dependency function) and is an
    administrator. If the user is not authenticated, is not enabled or is not an
    administrator, it raises an exception.

    Args:
        user (User): Authenticated and enabled user.

    Raises:
        HTTPException: If the user is not authenticated, is not enabled or is not an
            administrator.

    Returns:
        User: Current user (authenticated and enabled and an administrator).
    """
    if not user.staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INV_CRED,
        )

    return user
