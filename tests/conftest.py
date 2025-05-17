"""Team Copilot Tests - Configuration."""

from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch
from typing import Generator

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from team_copilot.main import app as _app
from team_copilot.models.data import User


@pytest.fixture
def app() -> FastAPI:
    """Get a FastAPI test client.

    Returns:
        TestClient: FastAPI test client.
    """
    return _app


@pytest.fixture
def test_client(app) -> TestClient:
    """Get a FastAPI test client.

    Returns:
        TestClient: FastAPI test client.
    """
    return TestClient(app)


@pytest.fixture
def mock_db_users() -> list[User]:
    """Mock a list of users for testing endpoints.

    Returns:
        list[User]: Mocked user objects.
    """
    now = datetime.now(timezone.utc)

    return [
        User(
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
        ),
        User(
            id=uuid4(),
            username="user2",
            password="user2user2",
            name="User 2",
            email="user2@example.com",
            staff=False,
            admin=False,
            enabled=True,
            created_at=now,
            updated_at=now,
        ),
    ]


@pytest.fixture
def mock_enabled_user() -> Generator[User, None, None]:
    """Mock an enabled user for testing endpoints.

    Returns:
        Generator[User, None, None]: Mocked user object.
    """
    now = datetime.now(timezone.utc)

    user = User(
        id=uuid4(),
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

    with patch("team_copilot.core.auth.get_enabled_user", return_value=user):
        yield user


@pytest.fixture
def mock_staff_user() -> Generator[User, None, None]:
    """Mock an enabled and staff user for testing endpoints.

    Returns:
        Generator[User, None, None]: Mocked user object.
    """
    now = datetime.now(timezone.utc)

    user = User(
        id=uuid4(),
        username="staff",
        password="staffstaff",
        name="Staff",
        email="staff@example.com",
        staff=True,
        admin=False,
        enabled=True,
        created_at=now,
        updated_at=now,
    )

    with patch("team_copilot.core.auth.get_enabled_user", return_value=user):
        yield user


@pytest.fixture
def mock_admin_user() -> Generator[User, None, None]:
    """Mock an enabled and administrator user for testing endpoints.

    Returns:
        Generator[User, None, None]: Mocked user object.
    """
    now = datetime.now(timezone.utc)

    user = User(
        id=uuid4(),
        username="admin",
        password="adminadmin",
        name="Admin",
        email="admin@example.com",
        staff=True,
        admin=True,
        enabled=True,
        created_at=now,
        updated_at=now,
    )

    with patch("team_copilot.core.auth.get_admin_user", return_value=user):
        yield user
