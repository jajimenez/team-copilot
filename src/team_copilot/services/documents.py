"""Team Copilot - Services - Documents."""

import logging

from team_copilot.db.session import open_session
from team_copilot.models.models import Document, DocumentChunk, DocumentStatus
from team_copilot.core.config import settings
from team_copilot.services.extraction import get_text
from team_copilot.services.embedding import get_embedding


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Messages
ERROR_PROC_DOC = 'Error processing document: "{}".'


def _save_doc(doc: Document):
    """Save a document to the database.

    Args:
        doc (Document): Document object.
    """
    with open_session(settings.app_db_url) as session:
        session.add(doc)
        session.commit()
        session.refresh(doc)


def process_doc(doc: Document):
    """Process a document that has been uploaded.

    Args:
        doc (Document): Document object.
    """
    try:
        # Set the document status
        doc.status = DocumentStatus.PROCESSING

        # Save the document to the database
        _save_doc(doc)

        # Extract the text chunks from the document
        chunks: list[str] = get_text(doc.path)

        # Get the embedding for each chunk and set the document chunks
        doc.chunks = [
            DocumentChunk(
                chunk_text=chunk,
                chunk_index=i,
                embedding=get_embedding(chunk),
            )
            for i, chunk in enumerate(chunks)
        ]

        # Set the document status
        doc.status = DocumentStatus.COMPLETED

        # Save the document to the database
        _save_doc(doc)

    except Exception as e:
        logger.error(ERROR_PROC_DOC.format(e))

        # Update the document status to Failed
        doc.status = DocumentStatus.FAILED
        _save_doc(doc)

        # Re-raise the exception
        raise
