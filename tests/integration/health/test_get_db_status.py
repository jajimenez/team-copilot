"""Team Copilot Tests - Integration Tests - Health - Get Database Status."""

from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from team_copilot.models.data import DbStatus


def test_get_db_status(test_client: TestClient):
    """Test the "get_db_status" endpoint when the database is available.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    with (
        patch("team_copilot.routers.health.check_status", return_value=True)
        as mock_check_status,
    ):
        # Make HTTP request
        response = test_client.get("/health/db")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        res_data = response.json()

        assert len(res_data) == 2
        assert res_data["message"] == "Database is available."

        data = res_data["data"]
        assert len(data) == 1
        assert data["status"] == DbStatus.AVAILABLE

        # Check function calls
        mock_check_status.assert_called_once()


def test_get_db_status_unavailable(test_client: TestClient):
    """Test the "get_db_status" endpoint when the database is unavailable.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    with (
        patch("team_copilot.routers.health.check_status", return_value=False)
        as mock_check_status,
    ):
        # Make HTTP request
        response = test_client.get("/health/db")

        # Check response
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        res_data = response.json()

        assert len(res_data) == 2
        assert res_data["message"] == "Database is unavailable."

        data = res_data["data"]
        assert len(data) == 1
        assert data["status"] == DbStatus.UNAVAILABLE

        # Check function calls
        mock_check_status.assert_called_once()
