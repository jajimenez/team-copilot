"""Team Copilot Tests - Integration Tests - Documents - Get All Documents."""

from unittest.mock import patch, MagicMock

from dateutil.parser import parse

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_staff_user
from team_copilot.models.data import User, Document

from tests.integration import raise_not_authorized_exc


@patch("team_copilot.routers.documents.get_all_docs")
def test_get_all_documents(
    mock_get_all_docs: MagicMock,
    app: FastAPI,
    test_client: TestClient, 
    test_staff_user: User,
    test_documents: list[Document],
):
    """Test the "get_all_documents" endpoint.

    Args:
        mock_get_all_docs (MagicMock): Mock object for the "get_all_docs" function.
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_staff_user (User): Test enabled staff user.
        test_documents (list[Document]): Test documents.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_staff_user] = lambda: test_staff_user

    # Mock the returned value of the "get_all_docs" function
    mock_get_all_docs.return_value = test_documents

    # Make HTTP request
    response = test_client.get("/documents")

    # Check response
    assert response.status_code == status.HTTP_200_OK

    doc_count = len(test_documents)
    res_data = response.json()

    assert len(res_data) == 3
    assert res_data["message"] == f"{doc_count} documents retrieved."
    assert res_data["count"] == doc_count

    data = res_data["data"]
    assert len(data) == doc_count

    for i, d in enumerate(data):
        assert d["id"] == str(test_documents[i].id)
        assert d["name"] == test_documents[i].name
        assert d["status"] == test_documents[i].status
        assert parse(d["created_at"]) == test_documents[i].created_at
        assert parse(d["updated_at"]) == test_documents[i].updated_at

    # Check functions call
    mock_get_all_docs.assert_called_once()

    # Clear simulated injected dependencies
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
    # Simulate injected dependencies
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

    # Clear simulated injected dependencies
    app.dependency_overrides.clear()
