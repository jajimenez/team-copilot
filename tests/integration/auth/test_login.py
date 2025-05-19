"""Team Copilot Tests - Integration Tests - Authentication - Login."""

from unittest.mock import patch, MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from team_copilot.models.data import User


@patch("team_copilot.routers.auth.authenticate_user")
def test_login(
    mock_authenticate_user: MagicMock,
    test_client: TestClient,
    test_users: list[User],
):
    """Test the "login" endpoint.

    Args:
        mock_authenticate_user (MagicMock): Mock object for the "authenticate_user"
            function.
        test_client (TestClient): FastAPI test client.
        test_users (list[User]): Test users.
    """
    # Mock the returned value of the "authenticate_user" function
    mock_authenticate_user.return_value = test_users[0]

    # Request data
    req_data = {"username": "user", "password": "password"}

    # Make HTTP request
    response = test_client.post("/auth/login", data=req_data)

    # Check response
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()

    assert len(res_data) == 2
    assert res_data["access_token"] is not None
    assert res_data["token_type"] == "bearer"

    # Check functions call
    mock_authenticate_user.assert_called_once_with(
        req_data["username"],
        req_data["password"],
    )


@patch("team_copilot.routers.auth.authenticate_user", return_value=None)
def test_login_invalid_credentials(
    mock_authenticate_user: MagicMock,
    test_client: TestClient,
):
    """Test the "login" endpoint with invalid credentials.

    Args:
        mock_authenticate_user (MagicMock): Mock object for the "authenticate_user"
            function.
        test_client (TestClient): FastAPI test client.
    """
    # Request data
    req_data = {"username": "user", "password": "password"}

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
    mock_authenticate_user.assert_called_once_with(
        req_data["username"],
        req_data["password"],
    )
