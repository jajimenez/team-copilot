"""Team Copilot - Routers - Authentication."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from team_copilot.models.models import Token
from team_copilot.core.config import Settings, get_settings
from team_copilot.core.auth import authenticate_user, create_access_token
from team_copilot.routers import INVALID_CREDENTIALS
from team_copilot.core.config import settings


# Messages
ACCESS_TOKEN = f"Access token (valid for {settings.app_acc_token_exp_min} minutes)" 

# Router
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    responses={
        status.HTTP_200_OK: {"description": ACCESS_TOKEN},
        status.HTTP_401_UNAUTHORIZED: {"description": INVALID_CREDENTIALS},
    },
    response_model=Token,
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Token:
    """Get an authentication token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data.
        settings (Settings): Application settings.

    Raises:
        HTTPException: If the credentials are invalid.

    Returns:
        Token: Token.
    """
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        headers = {"WWW-Authenticate": "Bearer"}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers=headers,
        )

    exp = timedelta(minutes=settings.app_acc_token_exp_min)
    token = create_access_token(data={"sub": user.username}, exp_delta=exp)

    return Token(access_token=token, token_type="bearer")
