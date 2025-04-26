"""Team Copilot - Agent - Tools."""

from langchain_core.tools import tool

from team_copilot.models.data import DocumentChunk
from team_copilot.services.search import get_most_similar_chunks


@tool(parse_docstring=True)
def search_docs(text: str) -> str:
    """Search for information in documents given a text.

    Args:
        text (str): Text to search for.

    Returns:
        str: Search result.
    """
    # Get the most similar chunks
    chunks: list[DocumentChunk] = get_most_similar_chunks(text)

    # Get the chunk texts
    chunks = [c.chunk_text for c in chunks]

    # Concatenate the chunks with a separator
    return "\n\n----\n\n".join(chunks)
