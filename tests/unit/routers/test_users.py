"""Team Copilot Tests - Unit Tests - Routers - Users."""

from unittest.mock import patch
from dateutil.parser import parse

from fastapi import FastAPI
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_admin_user
from team_copilot.models.data import User


def test_get_all_users(
    app: FastAPI,
    test_client: TestClient,
    mock_admin_user: User,
    mock_db_users: list[User],
):
    """Test get all users endpoint.

    Args:
        test_client (TestClient): FastAPI test client.
        mock_db_users (list[User]): Mocked user objects.
    """
    app.dependency_overrides[get_admin_user] = lambda: mock_admin_user

    with patch("team_copilot.routers.users.get_all_us", return_value=mock_db_users):
        response = test_client.get("/users")
        assert response.status_code == 200

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
