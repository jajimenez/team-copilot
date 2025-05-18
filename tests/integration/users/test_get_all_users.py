"""Team Copilot Tests - Integration Tests - Users - Get All Users."""

from unittest.mock import patch

from dateutil.parser import parse

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_admin_user
from team_copilot.models.data import User

from tests.integration import raise_not_authorized_exc


def test_get_all_users(
    app: FastAPI,
    test_client: TestClient,
    test_admin_user: User,
    test_users: list[User],
):
    """Test the "get_all_users" endpoint.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_admin_user (User): Mock enabled administrator user.
        test_users (list[User]): Test users.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_admin_user] = lambda: test_admin_user

    with patch(
        "team_copilot.routers.users.get_all_us",
        return_value=test_users,
    ) as mock_get_all_users:
        # Make HTTP request
        response = test_client.get("/users")

        # Check response
        assert response.status_code == status.HTTP_200_OK

        user_count = len(test_users)
        res_data = response.json()

        assert len(res_data) == 3
        assert res_data["message"] == f"{user_count} users retrieved."
        assert res_data["count"] == user_count

        data = res_data["data"]
        assert len(data) == user_count

        for i, u in enumerate(data):
            assert u["id"] == str(test_users[i].id)
            assert u["username"] == test_users[i].username
            assert u["name"] == test_users[i].name
            assert u["email"] == test_users[i].email
            assert u["staff"] == test_users[i].staff
            assert u["admin"] == test_users[i].admin
            assert u["enabled"] == test_users[i].enabled
            assert parse(u["created_at"]) == test_users[i].created_at
            assert parse(u["updated_at"]) == test_users[i].updated_at

        # Check function calls
        mock_get_all_users.assert_called_once()

    app.dependency_overrides.clear()


def test_get_all_users_unauthenticated(test_client: TestClient):
    """Test the "get_all_users" endpoint for an unauthenticated user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    # Make HTTP request
    response = test_client.get("/users")

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


def test_get_all_users_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "get_all_users" endpoint for an unauthorized (disabled or not
    administrator) user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_admin_user] = raise_not_authorized_exc

    # Make HTTP request
    response = test_client.get("/users")

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
