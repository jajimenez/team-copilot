"""Team Copilot - Services - Search."""

from sqlalchemy import text
from sqlmodel import select

from team_copilot.core.config import settings
from team_copilot.db.session import open_session
from team_copilot.models.data import DocumentChunk
from team_copilot.services.embedding import get_embedding


def get_most_similar_chunks(t: str, limit: int = 5) -> list[DocumentChunk]:
    """Get the most similar document chunks for a given text.

    Args:
        t (str): Text to search for.
        limit (int, optional): Maximum number of chunks to return (default: 5).

    Returns:
        list[DocumentChunk]: Most similar chunks ordered by similarity.
    """
    # Get the text embedding
    emb = get_embedding(t)

    with open_session(settings.db_url) as session:
        # Search for the closest chunks in the database

        # Create the statement. This is a raw SQL statement because the "<=>" operator
        # is specific to PostgreSQL and its vector extension and is not supported by
        # SQLModel. The "<=>" operator returns the distance between two vectors, which
        # is a number between 0 (identical) and 2 (completely different).

        # We format the statement string with the "emb" variable between single quotes,
        # which is the format of the "embedding" vector column in SQL statements. We
        # can't use the "params" argument of the "text" function because it doesn't
        # translate "emb" to the proper format.
        s = text(
            "SELECT dc.id "
            "FROM document_chunks dc "
            f"ORDER BY dc.embedding <=> '{emb}' "
            f"LIMIT {limit};"
        )

        rows = session.exec(s)
        chunk_ids = [r[0] for r in rows]

        if not chunk_ids:
            return []

        # Get the DocumentChunk objects

        # Create the statement
        s = select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))

        # Execute the statement and return the result
        return session.exec(s).all()
