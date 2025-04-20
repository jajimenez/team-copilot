"""Team Copilot - Services - Search."""

import logging

from sqlalchemy import text
from sqlmodel import select

from team_copilot.core.config import settings
from team_copilot.db.session import open_session
from team_copilot.models.data import DocumentChunk
from team_copilot.services.embedding import get_embedding


# Messages
NO_EMB_FOUND = 'No embedding found for text "{}".'
ERROR_GET_CHUNKS = 'Error getting similar chunks for text "{}": "{}".'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_most_similar_chunks(query: str, limit: int = 5) -> list[DocumentChunk]:
    """Get the most similar document chunks for a given text.

    Args:
        query (str): Text to search for.
        limit (int, optional): Maximum number of chunks to return (default: 5).

    Returns:
        list[DocumentChunk]: Most similar chunks ordered by similarity.
    """
    # Get the text embedding
    emb = get_embedding(query, "query")

    if not emb:
        error = NO_EMB_FOUND.format(query)
        logger.error(error)

        raise ValueError(error)

    # Search for the closest chunks in the database
    try:
        with open_session(settings.db_url) as session:
            # Create the statement. This is a raw SQL statement because the "<=>" operator
            # is specific to the "pgvector" extension of PostgreSQL and isn't supported by
            # SQLModel.

            # The "<=>" operator returns the cosine distance between two vectors,
            # which is a number between 0 (vectors are identical) and 2 (vectors point in
            # opposite directions). A value of 1 means that the vectors are perpendicular.
            # Therefore, the smaller the value, the more similar the vectors are.

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
    except Exception as e:
        error = ERROR_GET_CHUNKS.format(query, e)
        logger.error(error)

        # Re-raise the exception with the error message
        raise Exception(error)
