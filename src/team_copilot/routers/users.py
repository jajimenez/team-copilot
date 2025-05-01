"""Team Copilot - Routers - Health."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from fastapi.exceptions import RequestValidationError, HTTPException

from team_copilot.core.auth import get_enabled_user, get_admin_user
from team_copilot.models.data import User
from team_copilot.models.request import CreateUserRequest

from team_copilot.models.response import (
    MessageResponse,
    UserResponse,
    UserSavedResponse,
)

from team_copilot.services.users import get_user, save_user, delete_user
from team_copilot.routers import VAL_ERROR, UNAUTH


# Descriptions and messages
CRE_USER_DESC = "Create a user. Only administrator users are authorized."
CRE_USER_SUM = "Create a user"
CUR_USER = "Current user"
GET_CUR_USER_DESC = "Get the current authenticated user."
GET_CUR_USER_SUM = "Get the current authenticated user"
USER_CRE_1 = "User created."
USER_CRE_2 = "User {} ({}) created."
USER_EXISTS = "A user with the same username or e-mail address exists."
USER_UPD = "User updated."
USER_DATA = "User data."

# Router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": UNAUTH,
            "model": MessageResponse,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": VAL_ERROR,
            "model": MessageResponse,
        },
    },
)


@router.get(
    "/me",
    operation_id="get_current_user",
    summary=GET_CUR_USER_SUM,
    description=GET_CUR_USER_DESC,
    responses={status.HTTP_200_OK: {"description": CUR_USER}},
    response_model=UserResponse,
)
def get_current_user(user: Annotated[User, Depends(get_enabled_user)]) -> UserResponse:
    """Get the current authenticated user.

    The user must be authenticated and enabled.

    Args:
        user (User): Current user.

    Returns:
        UserResponse: Current user response.
    """
    return UserResponse.from_user(user)


@router.post(
    "/",
    operation_id="create_user",
    summary=CRE_USER_SUM,
    description=CRE_USER_DESC,
    dependencies=[Depends(get_admin_user)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": USER_CRE_1,
            "model": UserSavedResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": USER_EXISTS,
            "model": MessageResponse,
        },
    },
)
async def create_user(
    user: Annotated[CreateUserRequest, Form(description=USER_DATA)],
) -> UserSavedResponse:
    """Create a user.

    Args:
        user (CreateUserRequest): User data.

    Raises:
        RequestValidationError: If the any field is invalid.
        HTTPException: If another user with the same username or e-mail address exists.

    Returns:
        UserSavedResponse: ID of the user and a message.
    """
    # Check that another user with the same username or e-mail address doesn't exist
    if get_user(username=user.username, email=user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_EXISTS)

    # Create a new User object
    u: User = user.to_user()

    # Save the User object to the database. The ID of the user is set by the database
    # and is set in the User object by "save_doc".
    save_user(u)

    # Return the user ID and a message
    return UserSavedResponse(user_id=u.id, message=USER_CRE_2.format(u.id, u.username))
