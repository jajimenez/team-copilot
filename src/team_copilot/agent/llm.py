"""Team Copilot - Agent - LLM."""

from langchain_anthropic import ChatAnthropic
from team_copilot.core.config import settings


def get_llm() -> ChatAnthropic:
    """Get an LLM instance.

    Returns:
        ChatAnthropic: LLM instance.
    """
    return ChatAnthropic(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        max_retries=settings.llm_max_retries,
        timeout=settings.llm_timeout_sec,
    )
