"""Team Copilot - Routers - Authentication."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from team_copilot.core.config import Settings, settings, get_settings
from team_copilot.core.auth import authenticate_user, create_access_token
from team_copilot.models.response import MessageResponse, TokenResponse
from team_copilot.routers import VALIDATION_ERROR, INVALID_CREDENTIALS


# Messages
ACCESS_TOKEN = f"Access token (valid for {settings.app_acc_token_exp_min} minutes)"
TOKEN_RET = "Token retrieved successfully."

# API documentation
LOGIN_DESC = "Get an authentication token."

# Router
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    description=LOGIN_DESC,
    responses={
        status.HTTP_200_OK: {
            "description": ACCESS_TOKEN,
            "model": TokenResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": INVALID_CREDENTIALS,
            "model": MessageResponse,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": VALIDATION_ERROR,
            "model": MessageResponse,
        },
    },
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Get an authentication token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data.
        settings (Settings): Application settings.

    Raises:
        HTTPException: If the credentials are invalid.

    Returns:
        TokenResponse: Token.
    """
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        # Include the "WWW-Authenticate" header to inform about the authentication
        # method used.
        headers = {"WWW-Authenticate": "Bearer"}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers=headers,
        )

    exp = timedelta(minutes=settings.app_acc_token_exp_min)
    token = create_access_token(data={"sub": user.username}, exp_delta=exp)

    return TokenResponse(access_token=token, token_type="bearer")
