
"""Team Copilot Tests - Integration Tests - Chat - Query Agent."""

import json
from typing import Any

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from team_copilot.core.auth import get_enabled_user
from team_copilot.models.data import User
from team_copilot.agent.agent import Agent
from team_copilot.routers.chat import TEXT_EV_STR

from tests.integration import raise_not_authorized_exc


UTF_8 = "utf-8"
CONT_TYPE = f"{TEXT_EV_STR}; charset={UTF_8}"


def test_query_agent(
    app: FastAPI,
    test_client: TestClient,
    test_enabled_user: User,
    test_agent: Agent,
):
    """Test the "query_agent" endpoint.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
        test_enabled_user (User): Mock enabled user.
        test_agent (Agent): Agent mock.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_enabled_user] = lambda: test_enabled_user

    # Request headers
    headers = {"accept": TEXT_EV_STR}

    # Request data
    text = "Test query."
    req_data = {"text": text}

    # Make HTTP request
    response = test_client.post("/chat/", headers=headers, json=req_data)

    # Check response
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == CONT_TYPE

    # Expected keys in the data of each streaming response event
    event_data_keys = {"index": int, "last": bool, "text": str}

    # Check the response streaming response events
    for e in response.iter_lines():
        if e:
            data_str: str = e.split("data: ")[1]
            data: dict[str, Any] = json.loads(data_str)

            assert len(data) == 3

            # Check expected keys and types
            for k, t in event_data_keys.items():
                assert k in data
                assert isinstance(data[k], t)

            if data["last"]:
                break

    # Check function calls
    test_agent.query.assert_called_once_with(text)

    app.dependency_overrides.clear()


def test_query_agent_unauthenticated(test_client: TestClient):
    """Test the "query_agent" endpoint for an unauthenticated user.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    # Request headers
    headers = {"accept": TEXT_EV_STR}

    # Request data
    req_data = {"text": "Test query."}

    # Make HTTP request
    response = test_client.post("/chat/", headers=headers, json=req_data)

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


def test_query_agent_unauthorized(app: FastAPI, test_client: TestClient):
    """Test the "query_agent" endpoint for an unauthorized (disabled) user.

    Args:
        app (FastAPI): FastAPI application.
        test_client (TestClient): FastAPI test client.
    """
    # Simulate the injected dependency
    app.dependency_overrides[get_enabled_user] = raise_not_authorized_exc

    # Request headers
    headers = {"accept": TEXT_EV_STR}

    # Request data
    req_data = {"text": "Test query."}

    # Make HTTP request
    response = test_client.post("/chat/", headers=headers, json=req_data)

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
