"""Team Copilot Tests - Unit Tests - Routers - Users - Get All Users."""

from unittest.mock import patch

from dateutil.parser import parse

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_admin_user
from team_copilot.models.data import User

from tests.unit.routers import raise_not_authorized_exc


def test_get_all_users(
    app: FastAPI,
    test_client: TestClient,
    admin_user_mock: User,
    users_mock: list[User],
):
    """Test the "get_all_users" endpoint.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        admin_user_mock (User): Enabled administrator user mock.
        users_mock (list[User]): Users mock.
    """
    app.dependency_overrides[get_admin_user] = lambda: admin_user_mock

    with patch(
        "team_copilot.routers.users.get_all_us",
        return_value=users_mock,
    ) as get_all_us_mock:
        # Make HTTP request
        response = test_client.get("/users")

        # Check response
        assert response.status_code == status.HTTP_200_OK

        user_count = len(users_mock)
        res_data = response.json()

        assert len(res_data) == 3
        assert res_data["message"] == f"{user_count} users retrieved."
        assert res_data["count"] == user_count

        data = res_data["data"]
        assert len(data) == user_count

        for i, u in enumerate(data):
            assert u["id"] == str(users_mock[i].id)
            assert u["username"] == users_mock[i].username
            assert u["name"] == users_mock[i].name
            assert u["email"] == users_mock[i].email
            assert u["staff"] == users_mock[i].staff
            assert u["admin"] == users_mock[i].admin
            assert u["enabled"] == users_mock[i].enabled
            assert parse(u["created_at"]) == users_mock[i].created_at
            assert parse(u["updated_at"]) == users_mock[i].updated_at

        # Check function calls
        get_all_us_mock.assert_called_once()

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
