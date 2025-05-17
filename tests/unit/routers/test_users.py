"""Team Copilot Tests - Unit Tests - Routers - Users."""

from unittest.mock import patch
from dateutil.parser import parse

from fastapi import FastAPI, status, HTTPException
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_enabled_user, get_admin_user
from team_copilot.models.data import User


def test_get_all_users(
    app: FastAPI,
    test_client: TestClient,
    mock_admin_user: User,
    mock_db_users: list[User],
):
    """Test the "get_all_users" endpoint.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        mock_admin_user (User): Mocked administrator user object.
        mock_db_users (list[User]): Mocked user objects.
    """
    app.dependency_overrides[get_admin_user] = lambda: mock_admin_user

    with patch("team_copilot.routers.users.get_all_us", return_value=mock_db_users):
        response = test_client.get("/users")
        assert response.status_code == status.HTTP_200_OK

        user_count = len(mock_db_users)

        res_data = response.json()
        assert len(res_data) == 3
        assert res_data["message"] == f"{user_count} users retrieved."
        assert res_data["count"] == user_count

        data = res_data["data"]
        assert len(data) == user_count

        for i, u in enumerate(data):
            assert u["id"] == str(mock_db_users[i].id)
            assert u["username"] == mock_db_users[i].username
            assert u["name"] == mock_db_users[i].name
            assert u["email"] == mock_db_users[i].email
            assert u["staff"] == mock_db_users[i].staff
            assert u["admin"] == mock_db_users[i].admin
            assert u["enabled"] == mock_db_users[i].enabled
            assert parse(u["created_at"]) == mock_db_users[i].created_at
            assert parse(u["updated_at"]) == mock_db_users[i].updated_at

    app.dependency_overrides.clear()


def test_get_all_users_unauthicated(test_client: TestClient):
    """Test the "get_all_users" endpoint for an unauthenticated user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    response = test_client.get("/users")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    res_data = response.json()
    assert len(res_data) == 2
    assert res_data["message"] == "An error occurred."

    data = res_data["data"]
    assert data["error"] == "Not authenticated"


def test_get_all_users_unauthorized(test_client: TestClient):
    """Test the "get_all_users" endpoint for an unauthorized (disabled or not
    administrator) user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    with patch("team_copilot.routers.users.get_admin_user") as mock_get_admin_user:
        mock_get_admin_user.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    response = test_client.get("/users")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    res_data = response.json()
    assert len(res_data) == 2
    assert res_data["message"] == "An error occurred."

    data = res_data["data"]
    assert data["error"] == "Not authenticated"


def test_get_current_user(
    app: FastAPI,
    test_client: TestClient,
    mock_enabled_user: User,
):
    """Test the "get_current_user" endpoint.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        mock_enabled_user (User): Mocked enabled user object.
    """
    app.dependency_overrides[get_enabled_user] = lambda: mock_enabled_user

    with patch("team_copilot.routers.users.get_us", return_value=mock_enabled_user):
        response = test_client.get("/users/me")
        assert response.status_code == status.HTTP_200_OK

        res_data = response.json()
        assert len(res_data) == 2

        assert res_data["message"] == (
            f"User {mock_enabled_user.id} ({mock_enabled_user.username}) retrieved."
        )

        data = res_data["data"]

        assert data["id"] == str(mock_enabled_user.id)
        assert data["username"] == mock_enabled_user.username
        assert data["name"] == mock_enabled_user.name
        assert data["email"] == mock_enabled_user.email
        assert data["staff"] == mock_enabled_user.staff
        assert data["admin"] == mock_enabled_user.admin
        assert data["enabled"] == mock_enabled_user.enabled
        assert parse(res_data["data"]["created_at"]) == mock_enabled_user.created_at
        assert parse(res_data["data"]["updated_at"]) == mock_enabled_user.updated_at

    app.dependency_overrides.clear()


def test_get_current_user_unauthicated(test_client: TestClient):
    """Test the "get_current_user" endpoint for an unauthenticated user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    response = test_client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    res_data = response.json()
    assert len(res_data) == 2
    assert res_data["message"] == "An error occurred."

    data = res_data["data"]
    assert data["error"] == "Not authenticated"


def test_get_current_user_unauthorized(test_client: TestClient):
    """Test the "get_current_user" endpoint for an unauthorized (disabled) user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    with patch("team_copilot.routers.users.get_enabled_user") as mock_get_enabled_user:
        mock_get_enabled_user.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    response = test_client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    res_data = response.json()
    assert len(res_data) == 2
    assert res_data["message"] == "An error occurred."

    data = res_data["data"]
    assert data["error"] == "Not authenticated"
