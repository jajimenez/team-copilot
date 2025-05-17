"""Team Copilot - Routers - Health."""

from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body, status
from fastapi.exceptions import HTTPException

from team_copilot.core.auth import get_enabled_user, get_admin_user
from team_copilot.models.data import User
from team_copilot.models.request import Undefined, CreateUserRequest, UpdateUserRequest

from team_copilot.models.response import (
    Response, UserResponse, UserListResponse, UserCreatedResponse
)

from team_copilot.services.users import (
    get_all_users as get_all_us,
    get_user as get_us,
    save_user,
    delete_user as del_user,
)

from team_copilot.routers import VAL_ERROR, NOT_AUTHENTICATED, NOT_AUTHORIZED


# Descriptions and messages
CRE_USER_DESC = "Create a user. Only administrator users are authorized."
CRE_USER_SUM = "Create a user"
CUR_USER = "Current user"
DEL_USER_DESC = "Delete a user. Only staff users are authorized."
DEL_USER_SUM = "Delete a user"
GET_ALL_USERS_DESC = "Get all users. Only administrator users are authorized."
GET_ALL_USERS_SUM = "Get all users"
GET_CUR_USER_DESC = "Get the current authenticated user."
GET_CUR_USER_SUM = "Get the current authenticated user"

UPD_USER_DESC = (
    "Update a user (some or all fields). Only administrator users are authorized."
)

UPD_USER_SUM = "Update a user"
USER_CRE_1 = "User created"
USER_CRE_2 = "User {} ({}) created."
USER_DATA = "User data"
USER_DEL_1 = "User deleted"
USER_DEL_2 = "User {} ({}) deleted."
USER_EXISTS = "A user with the same username or e-mail address already exists."
USER_ID = "User ID"
USER_NF_1 = "User not found"
USER_NF_2 = "User {} not found."
USER_RET = "User {} ({}) retrieved."
USER_UPD_1 = "User updated"
USER_UPD_2 = "User {} ({}) updated."
USERS_DAT = "Users data"
USERS_RET_1 = "1 user retrieved."
USERS_RET_2 = "{} users retrieved."

# Router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": NOT_AUTHENTICATED,
            "model": Response,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": NOT_AUTHORIZED,
            "model": Response,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": VAL_ERROR,
            "model": Response,
        },
    },
)


@router.get(
    "/",
    operation_id="get_all_users",
    summary=GET_ALL_USERS_SUM,
    description=GET_ALL_USERS_DESC,
    dependencies=[Depends(get_admin_user)],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": USERS_DAT,
            "model": UserListResponse,
        },
    },
)
async def get_all_users() -> UserListResponse:
    """Get all users.

    Returns:
        UserListResponse: Message, user count and users.
    """
    # Get all the users from the database
    users = get_all_us()

    # Get user count and message
    count = len(users)
    message = USERS_RET_1 if count == 1 else USERS_RET_2.format(count)

    # Return message, user count and users.
    return UserListResponse.create(message=message, users=users)


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
async def get_current_user(user: Annotated[User, Depends(get_enabled_user)]) -> UserResponse:
    """Get the current authenticated user.

    The user must be authenticated and enabled.

    Args:
        user (User): Current user.

    Returns:
        UserResponse: Message and current user.
    """
    message = USER_RET.format(user.id, user.username)
    return UserResponse.create(message=message, user=user)


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
            "model": UserCreatedResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": USER_EXISTS,
            "model": Response,
        },
    },
)
async def create_user(
    user: Annotated[CreateUserRequest, Body(description=USER_DATA)],
) -> UserCreatedResponse:
    """Create a user.

    Args:
        user (CreateUserRequest): User data.

    Raises:
        RequestValidationError: If the any field is invalid.
        HTTPException: If another user with the same username or e-mail address exists.

    Returns:
        UserCreatedResponse: Message and user ID.
    """
    # Check that another user with the same username or e-mail address doesn't exist
    if get_us(username=user.username, email=user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_EXISTS)

    # Create a new User object
    u: User = user.to_user()

    # Save the User object to the database. The ID of the user is set by the database
    # and is set in the User object by "save_user".
    save_user(u)

    # Return message and user ID
    message = USER_CRE_2.format(u.id, u.username)
    return UserCreatedResponse.create(message=message, user=u)


@router.put(
    "/{id}",
    operation_id="update_user",
    summary=UPD_USER_SUM,
    description=UPD_USER_DESC,
    dependencies=[Depends(get_admin_user)],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": USER_UPD_1,
            "model": UserResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": USER_NF_1,
            "model": Response,
        },
        status.HTTP_409_CONFLICT: {
            "description": USER_EXISTS,
            "model": Response,
        },
    },
)
async def update_user(
    id: Annotated[UUID, Path(description=USER_ID)],
    user: Annotated[UpdateUserRequest, Body(description=USER_DATA)],
) -> UserResponse:
    """Update a user.

    Args:
        id (UUID): User ID.
        user (CreateUserRequest): User data.

    Raises:
        RequestValidationError: If the any field is invalid.
        HTTPException: If the user doesn't exist or another user with the same username
            or e-mail address exists.

    Returns:
        UserResponse: Message and user.
    """
    # Check that the user exists and get the user
    u = get_us(id=id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NF_2.format(id),
        )

    # If the username or e-mail address have been provided, check that another user with
    # the same username or e-mail address doesn't exist.
    username_prov = user.username is not Undefined
    email_prov = user.email is not Undefined

    if username_prov or email_prov:
        other_user = get_us(
            username=user.username if username_prov else None,
            email=user.email if email_prov else None,
        )

        if other_user and other_user.id != id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=USER_EXISTS,
            )

    # Update the User object for the provided fields
    for i in ["username", "password", "name", "email", "staff", "admin", "enabled"]:
        # Get the value of the field from the request user object
        val = getattr(user, i)

        # If the value has been provided (i.e. it's not Undefined), set the value of the
        # corresponding field in the existing user object to the provided value.
        if val is not Undefined:
            setattr(u, i, val)

    # Set the "updated_at" field to None to let the database update it to the current
    # timestamp when we save it to the database.
    u.updated_at = None

    # Save the existing user object to the database
    save_user(u)

    # Return message and user
    message = USER_UPD_2.format(u.id, u.username)
    return UserResponse.create(message=message, user=u)


@router.delete(
    "/{id}",
    operation_id="delete_user",
    summary=DEL_USER_SUM,
    description=DEL_USER_DESC,
    dependencies=[Depends(get_admin_user)],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": USER_DEL_1,
            "model": Response,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": USER_NF_1,
            "model": Response,
        },
    },
)
async def delete_user(
    id: Annotated[UUID, Path(description=USER_ID)],
) -> Response:
    """Delete a user.

    Args:
        id (UUID): User ID.

    Raises:
        HTTPException: If the user is not found.

    Returns:
        Response: Message.
    """
    try:
        # Get the user from the database
        user = get_us(id=id)

        # Check that the user exists
        if not user:
            raise ValueError()

        # Delete the user. A ValueError will be raised if the user doesn't exist
        # although this should never happen because we already checked that the user
        # exists.
        del_user(id)
    except ValueError:
        # Re-raise exception as HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NF_2.format(id),
        )

    # Return message
    message = USER_DEL_2.format(user.id, user.username)
    return Response(message=message)
