"""Team Copilot Tests - Integration Tests - Health - Get Application Status."""

from fastapi import status
from fastapi.testclient import TestClient

from team_copilot.models.data import AppStatus


def test_get_app_status(test_client: TestClient):
    """Test the "get_app_status" endpoint.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    # Make HTTP request
    response = test_client.get("/health/app")

    # Check response
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()

    assert len(res_data) == 2
    assert res_data["message"] == "Application is available."

    data = res_data["data"]
    assert len(data) == 1
    assert data["status"] == AppStatus.AVAILABLE
