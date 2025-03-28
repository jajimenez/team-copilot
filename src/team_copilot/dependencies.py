"""Team Copilot - Dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status

import jwt
from jwt.exceptions import InvalidTokenError

from team_copilot.models.models import TokenData, User, DbUser
from team_copilot.core.auth import oauth2_scheme, get_user
from team_copilot.core.config import settings


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

    user: DbUser | None = get_user(username=token_data.username)

    if user is None:
        raise cred_exc

    # Convert the DbUser instance to a User instance to remove the password hash
    return user.to_user()


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
