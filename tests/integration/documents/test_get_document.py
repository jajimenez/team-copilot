"""Team Copilot Tests - Integration Tests - Documents - Get Document."""

from uuid import uuid4
from unittest.mock import patch

from dateutil.parser import parse

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_staff_user
from team_copilot.models.data import User, Document

from tests.integration import raise_not_authorized_exc


def test_get_document(
    app: FastAPI,
    test_client: TestClient, 
    test_staff_user: User,
    test_documents: list[Document],
):
    """Test the "get_document" endpoint.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_staff_user (User): Mock enabled staff user.
        test_documents (list[Document]): Test documents.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_staff_user] = lambda: test_staff_user

    doc = test_documents[0]

    with patch(
        "team_copilot.routers.documents.get_doc",
        return_value=doc,
    ) as mock_get_doc:
        # Make HTTP request
        response = test_client.get(f"/documents/{doc.id}")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        res_data = response.json()

        assert len(res_data) == 2
        assert res_data["message"] == f"Document {doc.id} ({doc.name}) retrieved."

        data = res_data["data"]
        assert len(data) == 5

        assert data["id"] == str(doc.id)
        assert data["name"] == doc.name
        assert data["status"] == doc.status
        assert parse(data["created_at"]) == doc.created_at
        assert parse(data["updated_at"]) == doc.updated_at

        # Check functions call
        mock_get_doc.assert_called_once_with(id=doc.id)

    # Clear dependency overrides
    app.dependency_overrides.clear()


def test_get_document_unauthenticated(test_client: TestClient):
    """Test the "get_document" endpoint for an unauthenticated user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    # Simulate a document ID
    doc_id = uuid4()

    # Make HTTP request
    response = test_client.get(f"/documents/{doc_id}")

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


def test_get_document_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "get_document" endpoint for an unauthorized (disabled or not staff)
    user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_staff_user] = raise_not_authorized_exc

    # Simulate a document ID
    doc_id = uuid4()

    # Make HTTP request
    response = test_client.get(f"/documents/{doc_id}")

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


def test_get_document_not_found(
    app: FastAPI,
    test_client: TestClient,
    test_staff_user: User,
):
    """Test the "get_document" endpoint for a non-existing document.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_staff_user (User): Mock enabled staff user.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_staff_user] = lambda: test_staff_user

    # Simulate a document ID
    doc_id = uuid4()

    # Make HTTP request
    response = test_client.get(f"/documents/{doc_id}")

    # Check response
    assert response.status_code == status.HTTP_404_NOT_FOUND

    res_data = response.json()
    assert len(res_data) == 3

    assert res_data["count"] == 1
    assert res_data["message"] == "Error."

    data = res_data["data"]
    assert len(data) == 1

    assert data[0]["id"] == "error"
    assert data[0]["message"] == f"Document {doc_id} not found."

    # Clear dependency overrides
    app.dependency_overrides.clear()
