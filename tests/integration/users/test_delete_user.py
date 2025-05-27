"""Team Copilot Tests - Integration Tests - Users - Delete User."""

from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_admin_user
from team_copilot.models.data import User

from tests.integration import raise_not_authorized_exc


@patch("team_copilot.routers.users.get_us")
@patch("team_copilot.routers.users.del_user")
def test_delete_user(
    mock_del_user: MagicMock,
    mock_get_us: MagicMock,
    app: FastAPI,
    test_client: TestClient,
    test_admin_user: User,
):
    """Test the "delete_user" endpoint.
    
    Args:
        mock_del_user (MagicMock): Mock object for the "del_user" function.
        mock_get_us (MagicMock): Mock object for the "get_us" function.
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_admin_user (User): Test enabled administrator user.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_admin_user] = lambda: test_admin_user

    # Simulate an existing user
    user_id = uuid4()
    now = datetime.now(timezone.utc)

    user = User(
        id=user_id,
        username="user",
        password="useruser",
        name="User",
        email="user@example.com",
        staff=False,
        admin=False,
        enabled=True,
        created_at=now,
        updated_at=now,
    )

    # Mock the returned value of the "get_us" function
    mock_get_us.return_value = user

    # Make request
    response = test_client.delete(f"/users/{user_id}")

    # Check response
    assert response.status_code == status.HTTP_200_OK

    res_data = response.json()
    assert len(res_data) == 1
    assert res_data["message"] == f"User {user.id} ({user.username}) deleted."

    # Check function calls
    mock_get_us.assert_called_once_with(id=user_id)
    mock_del_user.assert_called_once_with(user_id)

    # Clear simulated injected dependencies
    app.dependency_overrides.clear()


def test_delete_user_unauthenticated(test_client: TestClient):
    """Test the "delete_user" endpoint for an unauthenticated user.
    
    Args:
        test_client (TestClient): FastAPI test client.
    """
    user_id = uuid4()

    # Make HTTP request
    response = test_client.delete(f"/users/{user_id}")

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


def test_delete_user_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "delete_user" endpoint for an unauthorized user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_admin_user] = raise_not_authorized_exc

    # Simulate the ID of an existing user
    user_id = uuid4()

    # Make HTTP request
    response = test_client.delete(f"/users/{user_id}")

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


@patch("team_copilot.routers.users.get_us", return_value=None)
def test_delete_user_not_found(
    mock_get_user: MagicMock,
    app: FastAPI,
    test_client: TestClient,
    test_admin_user: User,
):
    """Test the "delete_user" endpoint with a non-existing user.

    Args:
        mock_get_user (MagicMock): Mock object for the "get_us" function.
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_admin_user (User): Test enabled administrator user.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_admin_user] = lambda: test_admin_user

    # Simulate the ID of a non-existing user
    user_id = uuid4()

    # Make HTTP request
    response = test_client.delete(f"/users/{user_id}")

    # Check response
    assert response.status_code == status.HTTP_404_NOT_FOUND

    res_data = response.json()
    assert len(res_data) == 3

    assert res_data["message"] == "Error."
    assert res_data["count"] == 1
    assert res_data["data"][0]["id"] == "error"
    assert res_data["data"][0]["message"] == f"User {user_id} not found."

    # Check function calls
    mock_get_user.assert_called_once_with(id=user_id)

    # Clear simulated injected dependencies
    app.dependency_overrides.clear()
