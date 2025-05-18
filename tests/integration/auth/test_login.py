"""Team Copilot Tests - Integration Tests - Authentication - Login."""

from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from team_copilot.models.data import User


def test_login(test_client: TestClient, test_users: list[User]):
    """Test the "login" endpoint.

    Args:
        test_client (TestClient): FastAPI test client.
        test_users (list[User]): Test users.
    """
    # Request data
    req_data = {"username": "user", "password": "password"}

    with patch(
        "team_copilot.routers.auth.authenticate_user",
        return_value=test_users[0],
    ) as mock_auth_user:
        # Make HTTP request
        response = test_client.post("/auth/login", data=req_data)

        # Check response
        assert response.status_code == status.HTTP_200_OK
        res_data = response.json()

        assert len(res_data) == 2
        assert res_data["access_token"] is not None
        assert res_data["token_type"] == "bearer"

        # Check functions call
        mock_auth_user.assert_called_once_with(
            req_data["username"],
            req_data["password"],
        )


def test_login_invalid_credentials(test_client: TestClient):
    """Test the "login" endpoint with invalid credentials.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Request data
    req_data = {"username": "user", "password": "password"}

    with patch(
        "team_copilot.routers.auth.authenticate_user",
        return_value=None,
    ) as mock_auth_user:
        # Make HTTP request
        response = test_client.post("/auth/login", data=req_data)

        # Check response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        res_data = response.json()

        assert len(res_data) == 3
        assert res_data["message"] == "Authentication error."
        assert res_data["count"] == 1

        data = res_data["data"]
        assert len(data) == 1

        assert data[0]["id"] == "authentication"
        assert data[0]["message"] == "Invalid credentials"

        # Check functions call
        mock_auth_user.assert_called_once_with(
            req_data["username"],
            req_data["password"],
        )
