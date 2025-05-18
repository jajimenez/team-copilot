"""Team Copilot Tests - Integration Tests - Documents - Get All Documents."""

from unittest.mock import patch

from dateutil.parser import parse

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_staff_user
from team_copilot.models.data import User, Document

from tests.integration import raise_not_authorized_exc


def test_get_all_documents(
    app: FastAPI,
    test_client: TestClient, 
    staff_user_mock: User,
    documents_mock: list[Document],
):
    """Test the "get_all_documents" endpoint.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        staff_user_mock (User): Enabled staff user mock.
        documents_mock (list[Document]): Documents mock.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_staff_user] = lambda: staff_user_mock

    # Mock the get_all_documents service function
    with patch(
        "team_copilot.routers.documents.get_all_docs",
        return_value=documents_mock,
    ) as get_all_docs_mock:
        # Make HTTP request
        response = test_client.get("/documents")

        # Check response
        assert response.status_code == status.HTTP_200_OK

        doc_count = len(documents_mock)
        res_data = response.json()

        assert len(res_data) == 3
        assert res_data["message"] == f"{doc_count} documents retrieved."
        assert res_data["count"] == doc_count

        data = res_data["data"]
        assert len(data) == doc_count

        for i, d in enumerate(data):
            assert d["id"] == str(documents_mock[i].id)
            assert d["name"] == documents_mock[i].name
            assert d["status"] == documents_mock[i].status
            assert parse(d["created_at"]) == documents_mock[i].created_at
            assert parse(d["updated_at"]) == documents_mock[i].updated_at

        # Check functions call
        get_all_docs_mock.assert_called_once()

    # Clear dependency overrides
    app.dependency_overrides.clear()


def test_get_all_documents_unauthenticated(test_client: TestClient):
    """Test the "get_all_documents" endpoint for an unauthenticated user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    # Make HTTP request
    response = test_client.get("/documents")

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


def test_get_all_documents_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "get_all_documents" endpoint for an unauthorized (disabled or not staff)
    user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_staff_user] = raise_not_authorized_exc

    # Make HTTP request
    response = test_client.get("/documents")

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
