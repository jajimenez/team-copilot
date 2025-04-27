"""Team Copilot - Agent - Agent."""

from textwrap import dedent
from typing import Annotated, Generator
from typing_extensions import TypedDict

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from team_copilot.agent.llm import get_llm
from team_copilot.agent.tools import search_docs


SYS_MSG = dedent(
    """You are a document assistant that only answers questions based on the content of
    documents stored.

    Important instructions:
    - Never explain your reasoning process.
    - Always use the search_doc tool to find information before answering.
    - Only provide information found in the documents.
    - If you cannot find the answer, say something like "I don't know" instead of making
      up an answer.
    - Never use your general knowledge or make up answers.
    - Always answer in the same language as the question whenever possible. Otherwise,
      answer in English.
    """
)


class AgentState(TypedDict):
    """Agent state."""

    # Messages to be sent to the LLM, which will be updated by appending new messages to
    # the list instead of overwriting the entire list.
    messages: Annotated[list, add_messages]


class Agent:
    """Agent."""

    def __init__(self):
        """Initialize the agent."""

        # System message
        self.sys_msg = SYS_MSG

        # Tools
        tools = [search_docs]

        # LLM
        self.llm = get_llm().bind_tools(tools)

        # Graph builder
        builder = StateGraph(AgentState)

        # Nodes
        builder.add_node("call_llm", self.call_llm)
        builder.add_node("tools", ToolNode(tools))

        # Edges
        builder.add_conditional_edges("call_llm", tools_condition)
        builder.add_edge("tools", "call_llm")

        # Start node
        builder.set_entry_point("call_llm")

        # Compile the graph
        self.graph = builder.compile()

    def call_llm(self, state: AgentState) -> AgentState:
        """Call the LLM.

        Args:
            state (AgentState): Agent state.

        Returns:
            AgentState: Updated agent state.
        """
        # Add the system message to the state if it's not already there
        messages = state["messages"]

        if not messages or messages[0].type != "system":
            messages = [SystemMessage(content=self.sys_msg)] + messages

        msg = self.llm.invoke(messages)
        return {"messages": [msg]}

    def query(self, text: str) -> Generator[str, None, None]:
        """Query the agent in stream mode.

        Args:
            text (str): Query text.

        Yields:
            str: Response tokens.
        """
        # Check that the text is not null or empty
        if not text:
            raise ValueError("Query text cannot be null or empty.")

        inp = {"messages": [HumanMessage(content=text)]}

        for token, _ in self.graph.stream(inp, stream_mode="messages"):
            if (
                token.type == "AIMessageChunk"
                and hasattr(token, "content")
                and token.content
                and (token_txt := token.content[0].get("text"))
            ):
                yield token_txt
