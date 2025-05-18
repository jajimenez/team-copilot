"""Team Copilot Tests - Configuration."""

from uuid import uuid4
from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import patch
from typing import Generator

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from team_copilot.main import app as _app
from team_copilot.models.data import User, Document, DocumentStatus


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
def users_mock() -> list[User]:
    """Users mock for testing endpoints.

    Returns:
        list[User]: Users mock.
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
def enabled_user_mock() -> Generator[User, None, None]:
    """Enabled user mock for testing endpoints.

    Returns:
        Generator[User, None, None]: User mock.
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
def staff_user_mock() -> Generator[User, None, None]:
    """Enabled staff user mock for testing endpoints.

    Returns:
        Generator[User, None, None]: User mock.
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
def admin_user_mock() -> Generator[User, None, None]:
    """Enabled administrator user mock for testing endpoints.

    Returns:
        Generator[User, None, None]: User mock.
    """
    now = datetime.now(timezone.utc)

    user = User(
        id=uuid4(),
        username="admin",
        password="adminadmin",
        name="Administrator",
        email="admin@example.com",
        staff=True,
        admin=True,
        enabled=True,
        created_at=now,
        updated_at=now,
    )

    with patch("team_copilot.core.auth.get_admin_user", return_value=user):
        yield user


@pytest.fixture
def pdf_file_mock() -> BytesIO:
    """PDF file mock for testing endpoints.

    Returns:
        BytesIO: PDF file mock.
    """
    file = BytesIO(b"%PDF-1.5\nTest PDF.")
    file.name = "test.pdf"

    return file


@pytest.fixture
def documents_mock() -> list[Document]:
    """Documents mock for testing endpoints.

    Returns:
        list[Document]: Documents mock.
    """
    now = datetime.now(timezone.utc)

    return [
        Document(
            id=uuid4(),
            name="Document 1",
            status=DocumentStatus.PENDING,
            created_at=now,
            updated_at=now,
        ),
        Document(
            id=uuid4(),
            name="Document 2",
            status=DocumentStatus.PENDING,
            created_at=now,
            updated_at=now,
        ),
    ]
