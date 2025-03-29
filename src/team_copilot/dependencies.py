"""Team Copilot - Dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status

import jwt
from jwt.exceptions import InvalidTokenError

from team_copilot.models.models import TokenData, User, DbUser
from team_copilot.core.auth import oauth2_scheme, get_user
from team_copilot.core.config import settings


# Messages
INV_CRED = "Invalid credentials"


async def get_auth_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get the authenticated user."""
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=INV_CRED,
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

    user: DbUser | None = get_user(username=token_data.username)

    if user is None:
        raise cred_exc

    # Convert the DbUser instance to a User instance to remove the password hash
    return user.to_user()


async def get_enabled_user(user: Annotated[User, Depends(get_auth_user)]):
    """Get the authenticated and enabled user."""
    if not user.enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INV_CRED,
        )

    return user


async def get_staff_user(user: Annotated[User, Depends(get_enabled_user)]):
    """Get the authenticated, enabled and staff user."""
    if not user.staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INV_CRED,
        )

    return user
