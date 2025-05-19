"""Team Copilot Tests - Integration Tests - Users - Get User."""

from uuid import uuid4
from unittest.mock import patch, MagicMock

from dateutil.parser import parse

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_admin_user
from team_copilot.models.data import User

from tests.integration import raise_not_authorized_exc


@patch("team_copilot.routers.users.get_us")
def test_get_user(
    mock_get_us: MagicMock,
    app: FastAPI,
    test_client: TestClient, 
    test_admin_user: User,
    test_users: list[User],
):
    """Test the "get_user" endpoint.

    Args:
        mock_get_us (MagicMock): Mock object for the "get_us" function.
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_admin_user (User): Test enabled administrator user.
        test_users (list[User]): Test users.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_admin_user] = lambda: test_admin_user

    # Get a test user
    user = test_users[0]

    # Simulate the returned value of the "get_us" function
    mock_get_us.return_value = user

    # Make HTTP request
    response = test_client.get(f"/users/{user.id}")

    # Check response
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()

    assert len(res_data) == 2
    assert res_data["message"] == f"User {user.id} ({user.username}) retrieved."

    data = res_data["data"]
    assert len(data) == 9

    assert data["id"] == str(user.id)
    assert data["username"] == user.username
    assert data["name"] == user.name
    assert data["email"] == user.email
    assert data["staff"] == user.staff
    assert data["admin"] == user.admin
    assert data["enabled"] == user.enabled
    assert parse(data["created_at"]) == user.created_at
    assert parse(data["updated_at"]) == user.updated_at

    # Check functions call
    mock_get_us.assert_called_once_with(id=user.id)

    # Clear simulated injected dependencies
    app.dependency_overrides.clear()


def test_get_user_unauthenticated(test_client: TestClient):
    """Test the "get_user" endpoint for an unauthenticated user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    # Simulate a user ID
    user_id = uuid4()

    # Make HTTP request
    response = test_client.get(f"/users/{user_id}")

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


def test_get_user_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "get_user" endpoint for an unauthorized (disabled or not administrator)
    user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_admin_user] = raise_not_authorized_exc

    # Simulate a user ID
    user_id = uuid4()

    # Make HTTP request
    response = test_client.get(f"/users/{user_id}")

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


def test_get_user_not_found(
    app: FastAPI,
    test_client: TestClient,
    test_admin_user: User,
):
    """Test the "get_document" endpoint for a non-existing document.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_admin_user (User): Test enabled staff user.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_admin_user] = lambda: test_admin_user

    # Simulate a user ID
    user_id = uuid4()

    # Make HTTP request
    response = test_client.get(f"/users/{user_id}")

    # Check response
    assert response.status_code == status.HTTP_404_NOT_FOUND

    res_data = response.json()
    assert len(res_data) == 3

    assert res_data["count"] == 1
    assert res_data["message"] == "Error."

    data = res_data["data"]
    assert len(data) == 1

    assert data[0]["id"] == "error"
    assert data[0]["message"] == f"User {user_id} not found."

    # Clear dependency overrides
    app.dependency_overrides.clear()
