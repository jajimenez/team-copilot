"""Team Copilot - Services - Documents."""

import logging

from sqlmodel import select

from team_copilot.db.session import open_session
from team_copilot.models.models import Document, DocumentChunk, DocumentStatus
from team_copilot.core.config import settings
from team_copilot.services.extraction import get_text
from team_copilot.services.embedding import get_embedding


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Messages
PROC_DOC = "Processing document: {}..."
PROC_DOC_SUCCESS = "Document processed successfully: {}"
ERROR_PROC_DOC = 'Error processing document: "{}".'


def doc_exists(doc: Document) -> bool:
    """Return whether a document already exists in the database based on its title or
    its file path.

    Args:
        doc (Document): Document.

    Returns:
        bool: Wether the document exists.
    """
    with open_session(settings.db_url) as session:
        s = select(Document).where(
            (Document.title == doc.title) |
            (Document.path == doc.path)
        )

        return session.exec(s).first() is not None


def process_doc(doc: Document):
    """Process a document that has been uploaded.

    Args:
        doc (Document): Document object.
    """
    logger.info(PROC_DOC.format(doc.title))

    with open_session(settings.db_url) as session:
        try:
            # Add document to the session
            session.add(doc)

            # Set the document status
            doc.status = DocumentStatus.PROCESSING

            # Commit the changes to the database
            session.commit()

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

            # Commit the changes to the database
            session.commit()

            logger.info(PROC_DOC_SUCCESS.format(doc.title))
        except Exception as e:
            logger.error(ERROR_PROC_DOC.format(e))

            # Update the document status to Failed
            doc.status = DocumentStatus.FAILED

            # Commit the changes to the database
            session.commit()

            # Re-raise the exception
            raise
