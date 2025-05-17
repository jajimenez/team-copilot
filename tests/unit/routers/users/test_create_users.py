"""Team Copilot Tests - Unit Tests - Routers - Users - Create User."""

from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_admin_user
from team_copilot.models.data import User

from tests.unit.routers import raise_not_authorized_exc


def test_create_user(app: FastAPI, test_client: TestClient, admin_user_mock: User):
    """Test the "create_user" endpoint.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        admin_user_mock (User): Enabled administrator user mock.
    """
    app.dependency_overrides[get_admin_user] = lambda: admin_user_mock
    
    # Create a User object
    now = datetime.now(timezone.utc)

    user = User(
        id=uuid4(),
        username="newuser",
        password="newusernewuser",
        name="New User",
        email="newuser@example.com",
        staff=False,
        admin=False,
        enabled=True,
        created_at=now,
        updated_at=now,
    )
    
    # Request data
    data = {
        "username": "newuser",
        "password": "newusernewuser",
        "name": "New User",
        "email": "newuser@example.com",
        "staff": False,
        "admin": False,
        "enabled": True,
    }

    with (
        patch("team_copilot.routers.users.get_us", return_value=None) as get_user_mock,
        patch("team_copilot.routers.users.save_user") as save_user_mock,
    ):
        # Configure the "save_user" mock to modify the user object
        def side_effect(u: User):
            u.id = user.id
            u.created_at = user.created_at
            u.updated_at = user.updated_at
            
        save_user_mock.side_effect = side_effect
        
        # Make HTTP request
        response = test_client.post("/users", json=data)
        
        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        
        res_data = response.json()
        assert len(res_data) == 2
        assert res_data["message"] == f"User {user.id} ({user.username}) created."
        assert res_data["data"]["user_id"] == str(user.id)

        # Verify mock calls
        get_user_mock.assert_called_once()
        save_user_mock.assert_called_once()
    
    app.dependency_overrides.clear()


def test_create_user_unauthenticated(test_client: TestClient):
    """Test the "create_user" endpoint for an unauthenticated user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    # Make HTTP request
    response = test_client.post("/users")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    res_data = response.json()
    assert len(res_data) == 3

    assert res_data["message"] == "Authentication error."
    assert res_data["count"] == 1

    data = res_data["data"]
    assert len(data) == 1

    assert data[0]["id"] == "authentication"
    assert data[0]["message"] == "Not authenticated"


def test_create_user_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "create_user" endpoint for an unauthorized (disabled or not
    administrator) user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    app.dependency_overrides[get_admin_user] = raise_not_authorized_exc

    # Make HTTP request
    response = test_client.post("/users")
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


def test_create_user_user_exists_username(
    app: FastAPI,
    test_client: TestClient,
    admin_user_mock: User,
):
    """Test the "create_user" endpoint when a user with the same username already
    exists.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        admin_user_mock (User): Enabled administrator user mock.
    """
    app.dependency_overrides[get_admin_user] = lambda: admin_user_mock

    # Create a simulated existing user
    now = datetime.now(timezone.utc)

    user = User(
        id=uuid4(),
        username="user1",
        password="user1user1",
        name="User 1",
        email="user1@example.com",
        staff=False,
        admin=False,
        enabled=True,
        created_at=now,
        updated_at=now,
    )

    # Request data
    data = {
        "username": "user1",
        "password": "user2user2",
        "name": "User 2",
        "email": "user2@example.com",
    }

    with patch("team_copilot.routers.users.get_us", return_value=user):
        # Make HTTP request
        response = test_client.post("/users", json=data)
        assert response.status_code == status.HTTP_409_CONFLICT

        res_data = response.json()
        assert len(res_data) == 3

        assert res_data["message"] == "Error."
        assert res_data["count"] == 1

        data = res_data["data"]

        assert len(data) == 1
        assert data[0]["id"] == "error"

        assert data[0]["message"] == (
            "A user with the same username or e-mail address already exists."
        )


def test_create_user_user_exists_email(
    app: FastAPI,
    test_client: TestClient,
    admin_user_mock: User,
):
    """Test the "create_user" endpoint when a user with the same e-mail address already
    exists.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        admin_user_mock (User): Enabled administrator user mock.
    """
    app.dependency_overrides[get_admin_user] = lambda: admin_user_mock

    # Create a simulated existing user
    now = datetime.now(timezone.utc)

    user = User(
        id=uuid4(),
        username="user1",
        password="user1user1",
        name="User 1",
        email="user1@example.com",
        staff=False,
        admin=False,
        enabled=True,
        created_at=now,
        updated_at=now,
    )

    # Request data
    data = {
        "username": "user2",
        "password": "user2user2",
        "name": "User 2",
        "email": "user1@example.com",
    }

    with patch("team_copilot.routers.users.get_us", return_value=user):
        # Make HTTP request
        response = test_client.post("/users", json=data)
        assert response.status_code == status.HTTP_409_CONFLICT

        res_data = response.json()
        assert len(res_data) == 3

        assert res_data["message"] == "Error."
        assert res_data["count"] == 1

        data = res_data["data"]

        assert len(data) == 1
        assert data[0]["id"] == "error"

        assert data[0]["message"] == (
            "A user with the same username or e-mail address already exists."
        )
