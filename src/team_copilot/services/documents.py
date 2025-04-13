"""Team Copilot - Services - Documents."""

from os import remove
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
GET_DOC_ARG_ERROR = "At least one of the ID, title or path must be provided."
PROC_DOC = 'Processing document "{}" ("{}")...'
DOC_PROC = 'Document "{}" ("{}") processed.'
ERROR_PROC_DOC = 'Error processing document "{}" ("{}"): "{}".'
DOC_DELETED = 'Document "{}" ("{}") deleted.'
DOC_NOT_FOUND = 'Document "{}" not found.'
ERROR_DEL_DOC = 'Error deleting document "{}": "{}".'


def get_doc(
    id: str | None = None,
    title: str | None = None,
    path: str | None = None,
) -> Document | None:
    """Get a document by its ID, title or file path.

    Args:
        doc (Document): Document.

    Returns:
        bool: Wether the document exists.
    """
    if not id and not title and not path:
        raise ValueError(GET_DOC_ARG_ERROR)

    with open_session(settings.db_url) as session:
        s = select(Document).where(
            (Document.id == id) | (Document.title == title) | (Document.path == path)
        )

        return session.exec(s).first()


def process_doc(doc: Document):
    """Process a document that has been uploaded.

    Args:
        doc (Document): New or existing document.
    """
    logger.info(PROC_DOC.format(doc.id, doc.title))

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

            logger.info(DOC_PROC.format(doc.id, doc.title))
        except Exception as e:
            logger.error(ERROR_PROC_DOC.format(doc.id, doc.title, e))

            # Update the document status to Failed
            doc.status = DocumentStatus.FAILED

            # Commit the changes to the database
            session.commit()

            # Re-raise the exception
            raise


def delete_doc(id: str):
    """Delete a document from the database.

    Args:
        id (str): Document ID.

    Raises:
        ValueError: If the document is not found.
    """
    with open_session(settings.db_url) as session:
        # Check if the document exists
        doc = session.get(Document, id)

        if not doc:
            m = DOC_NOT_FOUND.format(id)
            logger.error(m)
            raise ValueError(m)

        try:
            # Delete the document from the database
            session.delete(doc)

            # Commit the changes to the database
            session.commit()

            # Delete the document file
            remove(doc.path)
        except Exception as e:
            logger.error(ERROR_DEL_DOC.format(doc.id, e))

            # Re-raise the exception
            raise

        logger.info(DOC_DELETED.format(doc.id, doc.title))
