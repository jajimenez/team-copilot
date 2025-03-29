"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, status

from team_copilot.models.models import User
from team_copilot.dependencies import get_enabled_user
from team_copilot.routers import UNAUTHORIZED


# Messages
CURRENT_USER = "Current user"

# Router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_enabled_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": UNAUTHORIZED}},
)


@router.get(
    "/me",
    responses={status.HTTP_200_OK: {"description": CURRENT_USER}},
    response_model=User,
)
def get_current_user(user: Annotated[User, Depends(get_enabled_user)]) -> User:
    """Get the current authenticated user.

    The user must be authenticated and its account must be enabled.

    Args:
        user (User): Current user.

    Returns:
        User: Current user.
    """
    return user
