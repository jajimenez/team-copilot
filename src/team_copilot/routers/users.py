"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, status

from team_copilot.models.models import User
from team_copilot.dependencies import get_current_act_user


# Router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_act_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"}},
)


@router.get("/me")
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
