"""Team Copilot Tests - Integration Tests - Users - Get Current User."""

from unittest.mock import patch, MagicMock

from dateutil.parser import parse

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_enabled_user
from team_copilot.models.data import User

from tests.integration import raise_not_authorized_exc


@patch("team_copilot.routers.users.get_us")
def test_get_current_user(
    mock_get_us: MagicMock,
    app: FastAPI,
    test_client: TestClient,
    test_enabled_user: User,
):
    """Test the "get_current_user" endpoint.

    Args:
        mock_get_us (MagicMock): Mock object for the "get_us" function.
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_enabled_user (User): Test enabled user.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_enabled_user] = lambda: test_enabled_user

    # Simulate the returned value of the "get_us" function
    mock_get_us.return_value = test_enabled_user

    # Make HTTP request
    response = test_client.get("/users/me")

    # Check response
    assert response.status_code == status.HTTP_200_OK

    res_data = response.json()
    assert len(res_data) == 2

    assert res_data["message"] == (
        f"User {test_enabled_user.id} ({test_enabled_user.username}) retrieved."
    )

    data = res_data["data"]

    assert data["id"] == str(test_enabled_user.id)
    assert data["username"] == test_enabled_user.username
    assert data["name"] == test_enabled_user.name
    assert data["email"] == test_enabled_user.email
    assert data["staff"] == test_enabled_user.staff
    assert data["admin"] == test_enabled_user.admin
    assert data["enabled"] == test_enabled_user.enabled
    assert parse(res_data["data"]["created_at"]) == test_enabled_user.created_at
    assert parse(res_data["data"]["updated_at"]) == test_enabled_user.updated_at

    # Clear simulated injected dependencies
    app.dependency_overrides.clear()


def test_get_current_user_unauthenticated(test_client: TestClient):
    """Test the "get_current_user" endpoint for an unauthenticated user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Make HTTP request
    response = test_client.get("/users/me")

    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    res_data = response.json()
    assert len(res_data) == 3

    assert res_data["message"] == "Authentication error."
    assert res_data["count"] == 1

    data = res_data["data"]
    assert len(data) == 1

    assert data[0]["id"] == "authentication"
    assert data[0]["message"] == "Not authenticated"


def test_get_current_user_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "get_current_user" endpoint for an unauthorized (disabled) user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_enabled_user] = raise_not_authorized_exc

    # Make HTTP request
    response = test_client.get("/users/me")

    # Check response
    assert response.status_code == status.HTTP_403_FORBIDDEN

    res_data = response.json()
    assert len(res_data) == 3

    assert res_data["message"] == "Authorization error."
    assert res_data["count"] == 1

    data = res_data["data"]
    assert len(data) == 1

    assert data[0]["id"] == "authorization"
    assert data[0]["message"] == "Not authorized"

    # Clear simulated injected dependencies
    app.dependency_overrides.clear()
