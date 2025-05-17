"""Team Copilot - Routers - Authentication."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from team_copilot.core.config import Settings, settings, get_settings
from team_copilot.core.auth import authenticate_user, create_access_token
from team_copilot.models.response import Response, TokenResponse
from team_copilot.routers import VAL_ERROR, INV_CRED


# Descriptions and messages
LOGIN_DESC = "Get an authentication token given a username and a password."
LOGIN_OUT_DESC = f"Access token (valid for {settings.app_acc_token_exp_min} minutes)"
LOGIN_SUM = "Login"

# By not using a SQLModel model as the input schema of the "login" endpoint, the FastAPI
# application object generates a schema name equal to the operation ID of the endpoint.
# Therefore, we need to rename the schemas in the OpenAPI documentation that the FastAPI
# application object generates (see the "team_copilot.main" module).

# Schemas to rename
SCHEMA_NAMES = {"Body_login": "LoginRequest"}

# Router
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    operation_id="login",
    summary=LOGIN_SUM,
    description=LOGIN_DESC,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": LOGIN_OUT_DESC,
            "model": TokenResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": INV_CRED,
            "model": Response,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": VAL_ERROR,
            "model": Response,
        },
    },
)
def login(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Get an authentication token given a username and a password.

    Args:
        login_data (OAuth2PasswordRequestForm): Login data.
        settings (Settings): Application settings.

    Raises:
        HTTPException: If the credentials are invalid.

    Returns:
        TokenResponse: Token and token type.
    """
    # Check credentials
    user = authenticate_user(login_data.username, login_data.password)

    if not user:
        # Include the "WWW-Authenticate" header to inform about the authentication
        # method used.
        headers = {"WWW-Authenticate": "Bearer"}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INV_CRED,
            headers=headers,
        )

    # Create the token
    exp = timedelta(minutes=settings.app_acc_token_exp_min)
    token = create_access_token(data={"sub": user.username}, exp_delta=exp)

    # Return the token and the token type
    return TokenResponse(access_token=token)
