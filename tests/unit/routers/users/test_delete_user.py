"""Team Copilot Tests - Unit Tests - Routers - Users - Delete User."""

from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch

from dateutil.parser import parse

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_admin_user
from team_copilot.models.data import User

from tests.unit.routers import raise_not_authorized_exc


def test_delete_user(app: FastAPI, test_client: TestClient, admin_user_mock: User):
    """Test the "delete_user" endpoint.
    
    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        admin_user_mock (User): Enabled administrator user mock.
    """
    app.dependency_overrides[get_admin_user] = lambda: admin_user_mock

    user_id = uuid4()
    now = datetime.now(timezone.utc)

    # Simulate an existing user
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

    with (
        patch("team_copilot.routers.users.get_us", return_value=user) as mock_get_us,
        patch("team_copilot.routers.users.del_user") as mock_del_user,
    ):
        # Make request
        response = test_client.delete(f"/users/{user_id}")

        # Check response
        assert response.status_code == status.HTTP_200_OK

        res_data = response.json()
        assert len(res_data) == 1
        assert res_data["message"] == f"User {user_id} ({user.username}) deleted."

        # Check function calls
        mock_get_us.assert_called_once_with(id=user_id)
        mock_del_user.assert_called_once_with(user_id)

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
    app.dependency_overrides[get_admin_user] = raise_not_authorized_exc
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

    app.dependency_overrides.clear()


def test_delete_user_not_found(
    app: FastAPI,
    test_client: TestClient,
    admin_user_mock: User,
):
    """Test the "delete_user" endpoint with a non-existing user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        admin_user_mock (User): Enabled administrator user mock.
    """
    app.dependency_overrides[get_admin_user] = lambda: admin_user_mock
    user_id = uuid4()

    with patch("team_copilot.routers.users.get_us", return_value=None) as get_us_mock:
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
        get_us_mock.assert_called_once_with(id=user_id)

    app.dependency_overrides.clear()
