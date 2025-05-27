"""Team Copilot - Services - Documents."""

from os import remove
from os.path import join, exists
from datetime import datetime, timezone
from uuid import UUID
import logging

from sqlmodel import select, or_

from team_copilot.db.session import open_session
from team_copilot.models.data import Document, DocumentStatus, DocumentChunk
from team_copilot.core.config import settings
from team_copilot.services.extraction import get_text
from team_copilot.services.embedding import get_embedding


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Messages
DOC_ALR_PROC = "Document {} ({}) already processed."
DOC_CRE = "Document {} ({}) created."
DOC_DEL = "Document {} ({}) deleted."
DOC_NF = "Document {} not found."
DOC_PROC = "Document {} ({}) processed."
DOC_UPD = "Document {} ({}) updated."
ERROR_DEL_DOC = "Error deleting document {} ({}): {}."
ERROR_PROC_DOC = "Error processing document {} ({}): {}."
GET_DOC_ARG = "At least, the ID or the name must be provided."
PROC_DOC = "Processing document {} ({})..."
TEMP_FILE_DEL = "Temporary PDF file ({}) of the document {} ({}) deleted."


def get_all_documents() -> list[Document]:
    """Get all documents.

    Returns:
        list[Document]: Documents.
    """
    with open_session(settings.db_url) as session:
        # Create statement
        s = select(Document)

        # Execute the statement and return all elements
        return session.exec(s).all()


def get_document(id: UUID | None = None, name: str | None = None) -> Document | None:
    """Get a document by its ID or name.

    Args:
        id (UUID | None): Document ID.
        name (str | None): Document name.

    Returns:
        Document | None: The document if it exists or None otherwise.
    """
    if not id and not name:
        raise ValueError(GET_DOC_ARG)

    with open_session(settings.db_url) as session:
        conditions = []

        if id is not None:
            conditions.append(Document.id == id)

        if name is not None:
            conditions.append(Document.name == name)

        # Create statement
        s = select(Document).where(or_(*conditions))

        # Execute the statement and return the first element
        return session.exec(s).first()


def get_document_file_path(doc_id: UUID) -> str:
    """Get the path of the temporary PDF file of a document given the document ID.

    Args:
        doc_id (UUID): Document ID.

    Returns:
        str: Temporary PDF file path.
    """
    return join(settings.app_temp_dir, f"{doc_id}.pdf")


def save_document(doc: Document):
    """Save a document to the database.

    If the document is new, the ID in the `Document` object is set to the ID generated
    automatically by the database server. If the document already exists, its
    "updated_at" field is updated to the current time.

    Args:
        doc (Document): Document to save.
    """
    with open_session(settings.db_url) as session:
        # Add document to the session
        session.add(doc)

        # Check if the document already exists (it exists if the ID in the Document
        # object is set). If it exists, update the "updated_at" field.
        if doc.id:
            update = True
            doc.updated_at = datetime.now(timezone.utc)
        else:
            update = False

        # Commit the changes to the database
        session.commit()

        if update:
            logger.info(DOC_UPD.format(doc.id, doc.name))
        else:
            logger.info(DOC_CRE.format(doc.id, doc.name))

        # Refresh the document to get the ID
        session.refresh(doc)


def process_document(id: UUID):
    """Process a document after its PDF file has been uploaded.

    When the document is processed, its PDF file is deleted.

    Args:
        id (UUID): Document ID.

    Raises:
        ValueError: If the document is not found or if the document has been already
            processed.
    """
    # Temporary PDF file path
    file_path = get_document_file_path(id)

    with open_session(settings.db_url) as session:
        try:
            # Get the document
            doc = session.get(Document, id)

            # Check that the document exists
            if not doc:
                raise ValueError(DOC_NF.format(id))

            logger.info(PROC_DOC.format(doc.id, doc.name))

            # Add document to the session
            session.add(doc)

            # Set the document status
            doc.status = DocumentStatus.PROCESSING

            # Commit the changes to the database
            session.commit()

            # Extract the text chunks from the PDF file
            text_chunks: list[str] = get_text(file_path)

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
                    embedding=get_embedding(tc, "document"),
                )

                session.add(c)

            # Set the document status
            doc.status = DocumentStatus.COMPLETED

            # Commit the changes to the database
            session.commit()
            logger.info(DOC_PROC.format(doc.id, doc.name))

            # Delete the temporary PDF file
            remove(file_path)
            logger.info(TEMP_FILE_DEL.format(file_path, doc.id, doc.name))
        except Exception as e:
            # Update the document status to Failed
            doc.status = DocumentStatus.FAILED

            # Commit the changes to the database
            session.commit()
            logger.error(ERROR_PROC_DOC.format(doc.id, doc.name, e))

            # Delete the temporary PDF file if it exists
            if exists(file_path):
                remove(file_path)
                logger.info(TEMP_FILE_DEL.format(file_path, doc.id, doc.name))

            # Re-raise the exception
            raise


def delete_document(id: UUID):
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
            m = DOC_NF.format(id)
            logger.error(m)

            raise ValueError(m)

        try:
            # Delete the document from the database
            session.delete(doc)

            # Commit the changes to the database
            session.commit()
            logger.info(DOC_DEL.format(doc.id, doc.name))

            # Delete the temporary PDF file if it exists
            file_path = get_document_file_path(doc.id)

            if exists(file_path):
                remove(file_path)
                logger.info(TEMP_FILE_DEL.format(file_path, doc.id, doc.name))
        except Exception as e:
            logger.error(ERROR_DEL_DOC.format(doc.id, doc.name, e))

            # Re-raise the exception
            raise
