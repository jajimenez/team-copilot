"""Team Copilot - Routers - Health."""

from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Path, status
from fastapi.exceptions import RequestValidationError, HTTPException



from team_copilot.core.auth import get_enabled_user, get_admin_user
from team_copilot.models.data import User
from team_copilot.models.request import CreateUserRequest, UpdateUserRequest

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
UPD_USER_DESC = "Update a user. Only administrator users are authorized."
UPD_USER_SUM = "Update a user"
USER_CRE_1 = "User created."
USER_CRE_2 = "User {} ({}) created."
USER_DATA = "User data."
USER_EXISTS = "A user with the same username or e-mail address exists."
USER_ID = "User ID."
USER_NF_1 = "User not found."
USER_NF_2 = "User {} not found."
USER_UPD = "User updated."

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
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": CUR_USER,
            "model": UserResponse,
        }
    },
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


@router.put(
    "/{id}",
    operation_id="update_user",
    summary=UPD_USER_SUM,
    description=UPD_USER_DESC,
    dependencies=[Depends(get_admin_user)],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": USER_UPD,
            "model": UserSavedResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": USER_NF_1,
            "model": MessageResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": USER_EXISTS,
            "model": MessageResponse,
        },
    },
)
async def update_user(
    id: Annotated[UUID, Path(description=USER_ID)],
    user: Annotated[UpdateUserRequest, Form(description=USER_DATA)],
) -> UserSavedResponse:
    """Update a user.

    Args:
        id (UUID): User ID.
        user (CreateUserRequest): User data.

    Raises:
        RequestValidationError: If the any field is invalid.
        HTTPException: If another user with the same username or e-mail address exists.

    Returns:
        UserSavedResponse: ID of the user and a message.
    """
    # Check that the user exists and get it
    u = get_user(id=id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NF_2.format(id),
        )

    # Check that another user with the same username or e-mail address doesn't exist
    other_user = get_user(username=user.username, email=user.email)

    if other_user and other_user.id != id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_EXISTS)

    # Update the User object. We set the "updated_at" field to None to let the database
    # set it to the current timestamp when we save it to the database.
    u.username = user.username
    u.name = user.name
    u.email = user.email
    u.staff = user.staff
    u.admin = user.admin
    u.enabled = user.enabled
    u.updated_at = None

    # Save the User object to the database
    save_user(u)

    # Return the user ID and a message
    return UserSavedResponse(user_id=u.id, message=USER_CRE_2.format(u.id, u.username))
