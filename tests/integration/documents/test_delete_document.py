"""Team Copilot Tests - Integration Tests - Documents - Delete Document."""

from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_staff_user
from team_copilot.models.data import User, Document, DocumentStatus

from tests.integration import raise_not_authorized_exc


def test_delete_document(app: FastAPI, test_client: TestClient, staff_user_mock: User):
    """Test the "delete_document" endpoint.
    
    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        staff_user_mock (User): Enabled staff user mock.
    """
    app.dependency_overrides[get_staff_user] = lambda: staff_user_mock

    doc_id = uuid4()
    now = datetime.now(timezone.utc)

    # Simulate an existing document
    doc = Document(
        id=doc_id,
        name="Document",
        status=DocumentStatus.COMPLETED,
        created_at=now,
        updated_at=now,
    )

    with (
        patch(
            "team_copilot.routers.documents.get_doc",
            return_value=doc,
        ) as get_doc_mock,
        patch("team_copilot.routers.documents.del_doc") as del_doc_mock,
    ):
        # Make request
        response = test_client.delete(f"/documents/{doc_id}")

        # Check response
        assert response.status_code == status.HTTP_200_OK

        res_data = response.json()
        assert len(res_data) == 1
        assert res_data["message"] == f"Document {doc.id} ({doc.name}) deleted."

        # Check function calls
        get_doc_mock.assert_called_once_with(id=doc_id)
        del_doc_mock.assert_called_once_with(doc_id)

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

    app.dependency_overrides.clear()


def test_delete_document_not_found(
    app: FastAPI,
    test_client: TestClient,
    staff_user_mock: User,
):
    """Test the "delete_document" endpoint with a non-existing document.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        staff_user_mock (User): Enabled staff user mock.
    """
    app.dependency_overrides[get_staff_user] = lambda: staff_user_mock
    doc_id = uuid4()

    with patch(
        "team_copilot.routers.documents.get_doc",
        return_value=None,
    ) as get_doc_mock:
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
        get_doc_mock.assert_called_once_with(id=doc_id)

    app.dependency_overrides.clear()
