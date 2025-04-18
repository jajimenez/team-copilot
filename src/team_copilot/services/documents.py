"""Team Copilot - Services - Documents."""

from os import remove
from datetime import datetime, timezone
from uuid import UUID
import logging

from sqlmodel import select

from team_copilot.db.session import open_session
from team_copilot.models.data import Document, DocumentStatus, DocumentChunk
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


def save_doc(doc: Document):
    """Save a document to the database.

    If the document is new, the ID in the database object is set to the ID generated
    automatically by the database server. If the document already exists, its
    "updated_at" field is updated to the current time.

    Args:
        doc (Document): Document to save.
    """
    with open_session(settings.db_url) as session:
        # Add document to the session
        session.add(doc)

        # Set the status to Pending
        doc.status = DocumentStatus.PENDING

        # Check if the document already exists (it exists if the ID in the document
        # object is set). If it exists, update the "updated_at" field.
        if doc.id:
            doc.updated_at = datetime.now(timezone.utc)

        # Commit the changes to the database
        session.commit()

        # Refresh the document to get the ID
        session.refresh(doc)


def get_doc(
    id: UUID | None = None,
    title: str | None = None,
    path: str | None = None,
) -> Document | None:
    """Get a document by its ID, title or file path.

    Args:
        id (UUID | None): Document ID.
        title (str | None): Document title.
        path (str | None): Document file path.

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


def process_doc(id: UUID):
    """Process a document.

    Args:
        id (UUID): Document ID.

    Raises:
        ValueError: If the document is not found.
    """
    with open_session(settings.db_url) as session:
        try:
            # Get the document
            doc = session.get(Document, id)

            # Check that the document exists
            if not doc:
                raise ValueError(DOC_NOT_FOUND.format(id))

            logger.info(PROC_DOC.format(doc.id, doc.title))

            # Add document to the session
            session.add(doc)

            # Set the document status
            doc.status = DocumentStatus.PROCESSING

            # Commit the changes to the database
            session.commit()

            # Extract the text chunks from the document
            text_chunks: list[str] = get_text(doc.path)

            # Delete the existing chunks from the database if any
            if doc.chunks:
                for c in doc.chunks:
                    session.delete(c)

                # Commit the changes to the database
                session.commit()

            # Get the embedding for each chunk and create the document chunks
            for i, tc in enumerate(text_chunks):
                c = DocumentChunk(
                    document_id=doc.id,
                    chunk_text=tc,
                    chunk_index=i,
                    embedding=get_embedding(tc),
                )

                session.add(c)

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


def delete_doc(id: UUID):
    """Delete a document from the database.

    Args:
        id (UUID): Document ID.

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
