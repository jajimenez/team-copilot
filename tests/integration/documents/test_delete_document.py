"""Team Copilot Tests - Integration Tests - Documents - Delete Document."""

from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_staff_user
from team_copilot.models.data import User, Document, DocumentStatus

from tests.integration import raise_not_authorized_exc


@patch("team_copilot.routers.documents.get_doc")
@patch("team_copilot.routers.documents.del_doc")
def test_delete_document(
    mock_del_doc: MagicMock,
    mock_get_doc: MagicMock,
    app: FastAPI,
    test_client: TestClient,
    test_staff_user: User,
):
    """Test the "delete_document" endpoint.

    Args:
        mock_del_doc (MagicMock): Mock object for the "del_doc" function.
        mock_get_doc (MagicMock): Mock object for the "get_doc" function.
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_staff_user (User): Test enabled staff user.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_staff_user] = lambda: test_staff_user

    # Simulate an existing document
    doc_id = uuid4()
    now = datetime.now(timezone.utc)

    doc = Document(
        id=doc_id,
        name="Document",
        status=DocumentStatus.COMPLETED,
        created_at=now,
        updated_at=now,
    )

    # Mock the returned value of the "get_doc" function
    mock_get_doc.return_value = doc

    # Make request
    response = test_client.delete(f"/documents/{doc_id}")

    # Check response
    assert response.status_code == status.HTTP_200_OK

    res_data = response.json()
    assert len(res_data) == 1
    assert res_data["message"] == f"Document {doc.id} ({doc.name}) deleted."

    # Check function calls
    mock_get_doc.assert_called_once_with(id=doc_id)
    mock_del_doc.assert_called_once_with(doc_id)

    # Clear simulated injected dependencies
    app.dependency_overrides.clear()


def test_delete_document_unauthenticated(test_client: TestClient):
    """Test the "delete_document" endpoint for an unauthenticated user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    doc_id = uuid4()

    # Make request
    response = test_client.delete(f"/documents/{doc_id}")

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


def test_delete_document_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "delete_document" endpoint for an unauthorized user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_staff_user] = raise_not_authorized_exc

    doc_id = uuid4()

    # Make request
    response = test_client.delete(f"/documents/{doc_id}")

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


@patch("team_copilot.routers.documents.get_doc", return_value=None)
def test_delete_document_not_found(
    mock_get_doc: MagicMock,
    app: FastAPI,
    test_client: TestClient,
    test_staff_user: User,
):
    """Test the "delete_document" endpoint with a non-existing document.

    Args:
        mock_get_doc (MagicMock): Mock object for the "get_doc" function.
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_staff_user (User): Test enabled staff user.
    """
    # Simulate injected dependencies
    app.dependency_overrides[get_staff_user] = lambda: test_staff_user

    # Simulate the ID of a non-existing document
    doc_id = uuid4()

    # Make HTTP request
    response = test_client.delete(f"/documents/{doc_id}")
    
    # Check response
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    res_data = response.json()
    assert len(res_data) == 3

    assert res_data["message"] == "Error."
    assert res_data["count"] == 1
    assert res_data["data"][0]["id"] == "error"
    assert res_data["data"][0]["message"] == f"Document {doc_id} not found."

    # Check function calls
    mock_get_doc.assert_called_once_with(id=doc_id)

    # Clear simulated injected dependencies
    app.dependency_overrides.clear()
