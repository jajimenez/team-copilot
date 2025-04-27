"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from team_copilot.models.data import User
from team_copilot.models.response import UserResponse, MessageResponse
from team_copilot.dependencies import get_enabled_user
from team_copilot.routers import UNAUTH


# Descriptions and messages
GET_CUR_USER_SUM = "Get the current authenticated user"
GET_CUR_USER_DESC = f"{GET_CUR_USER_SUM}."
CURRENT_USER = "Current user"

# Router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_enabled_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": UNAUTH,
            "model": MessageResponse,
        },
    },
)


@router.get(
    "/me",
    operation_id="get_current_user",
    summary=GET_CUR_USER_SUM,
    description=GET_CUR_USER_DESC,
    responses={status.HTTP_200_OK: {"description": CURRENT_USER}},
    response_model=UserResponse,
)
def get_current_user(user: Annotated[User, Depends(get_enabled_user)]) -> UserResponse:
    """Get the current authenticated user.

    The user must be authenticated and its account must be enabled.

    Args:
        user (User): Current user.

    Returns:
        UserResponse: Current user response.
    """
    return UserResponse.from_user(user)
