"""Team Copilot Tests - Integration Tests - Health - Get Database Status."""

from unittest.mock import patch, MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from team_copilot.models.data import DbStatus


@patch("team_copilot.routers.health.check_status", return_value=True)
def test_get_db_status(mock_check_status: MagicMock, test_client: TestClient):
    """Test the "get_db_status" endpoint when the database is available.

    Args:
        mock_check_status (MagicMock): Mock object for the "check_status" function.
        test_client (TestClient): FastAPI test client.
    """
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


@patch("team_copilot.routers.health.check_status", return_value=False)
def test_get_db_status_unavailable(
    mock_check_status: MagicMock,
    test_client: TestClient,
):
    """Test the "get_db_status" endpoint when the database is unavailable.

    Args:
        mock_check_status (MagicMock): Mock object for the "check_status" function.
        test_client (TestClient): FastAPI test client.
    """
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
