"""Team Copilot - Routers - Chat."""

from textwrap import dedent

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from team_copilot.models.response import MessageResponse
from team_copilot.dependencies import get_enabled_user
from team_copilot.models.request import AgentQueryRequest
from team_copilot.models.response import AgentResponseChunk
from team_copilot.agent.agent import Agent
from team_copilot.routers import VAL_ERROR, UNAUTH


# Descriptions and messages
AGENT_RES_CHUNK = dedent(
    """Agent response chunk. Each chunk is a string containing "data: " followed by the
    actual data in JSON format ({"index": string, "last": boolean, "text": string}) and
    followed by two newline characters. The last chunk has "index" set to -1, "last" set
    to true and "text" set to an empty string."""
)

QUERY_AGENT_DESC = (
    "Ask the agent a question about the documents and get a streaming response."
)

QUERY_AGENT_SUM = "Query the agent"

# Responses
AGENT_RES_EVENT = "data: {}\n\n"
TEXT_EVENT_STREAM = "text/event-stream"

# Examples
chunk_ex = AgentResponseChunk(index=0, last=False, text="Text chunk")
AGENT_RES_EX = AGENT_RES_EVENT.format(chunk_ex.model_dump_json(indent=2))

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
            "description": AGENT_RES_CHUNK,
            "content": {TEXT_EVENT_STREAM: {"example": AGENT_RES_EX}},
        },
    },
    response_class=StreamingResponse,
)
async def query_agent(query: AgentQueryRequest) -> StreamingResponse:
    """Query the agent and get a streaming response.

    The response follows the Server-Sent Events (SSE) format, being returned as a stream
    of events. The data of each event is a string containing "data: " followed by the
    actual data in JSON format ({"index": string, "last": boolean, "text": string}) and
    followed by two newline characters. The JSON data of the last event has "index" set
    to -1, "last" set to true and "text" set to an empty string.

    Args:
        query (AgentQueryRequest): Query to send to the agent.

    Returns:
        StreamingResponse: Response chunk from the agent.
    """

    async def get_response_gen(agent: Agent, text: str):
        """Get a generator to yield agent response chunks."""
        # Query the agent and yield each response chunk
        for i, res in enumerate(agent.query(text)):
            chunk = AgentResponseChunk(index=i, last=False, text=res)
            yield AGENT_RES_EVENT.format(chunk.model_dump_json())

        # Yield the last chunk to indicate completion
        last_chunk = AgentResponseChunk(index=-1, last=True, text="")
        yield AGENT_RES_EVENT.format(last_chunk.model_dump_json())

    # Create an agent instance
    agent = Agent()

    return StreamingResponse(
        get_response_gen(agent, query.text),
        media_type=TEXT_EVENT_STREAM,
    )
