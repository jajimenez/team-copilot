"""Team Copilot - Routers - Chat."""

from textwrap import dedent

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from team_copilot.core.auth import get_enabled_user
from team_copilot.models.request import AgentQueryRequest
from team_copilot.models.response import MessageResponse, AgentResponseChunk
from team_copilot.agent.agent import Agent
from team_copilot.routers import VAL_ERROR, UNAUTH


# Descriptions and messages
AGENT_RES = dedent(
    """Stream of events with the Server-Sent Events (SSE) format. Each event is a string
    containing "data: " followed by the actual event data in JSON format
    ({"index": string, "last": boolean, "text": string}) and followed by two newline
    characters. The data of the last event has "index" set to -1, "last" set to true and
    "text" set to an empty string."""
)

QUERY_AGENT_DESC = (
    "Ask the agent a question about the documents and get a streaming response."
)

QUERY_AGENT_SUM = "Query the agent"

# Responses
TEXT_EVENT_STREAM = "text/event-stream"

# Examples
chunk_ex: str = AgentResponseChunk(index=0, last=False, text="Text chunk").to_sse()

# Router
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(get_enabled_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": UNAUTH,
            "model": MessageResponse,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": VAL_ERROR,
            "model": MessageResponse,
        },
    },
)


@router.post(
    "/",
    operation_id="query_agent",
    summary=QUERY_AGENT_SUM,
    description=QUERY_AGENT_DESC,
    responses={
        status.HTTP_200_OK: {
            "description": AGENT_RES,
            "content": {TEXT_EVENT_STREAM: {"example": chunk_ex}},
        },
    },
    response_class=StreamingResponse,
)
async def query_agent(query: AgentQueryRequest) -> StreamingResponse:
    """Query the agent and get a streaming response.

    The response is a stream of events with the Server-Sent Events (SSE) format. Each
    event is a string containing "data: " followed by the actual event data in JSON
    format ({"index": string, "last": boolean, "text": string}) and followed by two
    newline characters. The data of the last event has "index" set to -1, "last" set to
    true and "text" set to an empty string.

    Args:
        query (AgentQueryRequest): Query to send to the agent.

    Returns:
        StreamingResponse: Response chunk from the agent.
    """

    async def get_response_gen(agent: Agent, text: str):
        """Get a generator to yield agent response chunks."""
        # Query the agent and yield each response chunk
        for i, res in enumerate(agent.query(text)):
            yield AgentResponseChunk(index=i, last=False, text=res).to_sse()

        # Yield the last chunk to indicate completion
        yield AgentResponseChunk(index=-1, last=True, text="").to_sse()

    # Create an agent instance
    agent = Agent()

    return StreamingResponse(
        get_response_gen(agent, query.text),
        media_type=TEXT_EVENT_STREAM,
    )
