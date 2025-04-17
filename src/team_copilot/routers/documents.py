"""Team Copilot - Routers - Documents."""

from os import makedirs, remove
from os.path import join, exists
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    BackgroundTasks,
    status,
    HTTPException,
)

from team_copilot.models.models import Document, Message, DocumentStatusMessage
from team_copilot.dependencies import get_staff_user
from team_copilot.services.documents import get_doc, process_doc, delete_doc
from team_copilot.core.config import Settings, get_settings, settings
from team_copilot.routers import UNAUTHORIZED


# Files
DOC_MIME_TYPE = "application/pdf"

# Messages
max_size_mb = settings.app_docs_max_size_bytes // (1024 * 1024)

DOC_ACCEPTED = "Document accepted."
NO_FILE_NAME = "The file does not have a name."
UNSUPPORTED_FILE_TYPE = "Unsupported file type (only PDF files are allowed)."
DOC_EXISTS = "A document with the same title or file name already exists."
FILE_TOO_LARGE = f"The file size exceeds the maximum limit ({max_size_mb} MB)."
ERROR_UPL_DOC = 'Error uploading document "{}".'
DOC_DELETED_1 = "Document deleted."
DOC_DELETED_2 = 'Document "{}" deleted.'
DOC_NOT_FOUND_1 = "Document not found."
DOC_NOT_FOUND_2 = 'Document "{}" not found.'
ERROR_DEL_DOC = 'Error deleting document "{}".'


# Router
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_staff_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": UNAUTHORIZED}},
)


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {"description": DOC_ACCEPTED},
        status.HTTP_409_CONFLICT: {"description": DOC_EXISTS},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"description": UNSUPPORTED_FILE_TYPE},
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {"description": FILE_TOO_LARGE},
    },
    response_model=DocumentStatusMessage,
)
async def create_document(
    title: str,
    file: Annotated[UploadFile, File(description="PDF file to upload")],
    bg_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentStatusMessage:
    """Create a document.

    Args:
        title (str): Document title.
        file (UploadFile): PDF file.
        bg_tasks (BackgroundTasks): Background tasks.
        settings (Settings): Application settings.
        response (Response): Response.

    Raises:
        HTTPException: If the file type is not supported or the file name is missing.

    Returns:
        DocumentStatus: Document status.
    """
    # Check that the file has a name
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=NO_FILE_NAME,
        )

    # Validate file type
    if file.content_type != DOC_MIME_TYPE:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=UNSUPPORTED_FILE_TYPE,
        )

    # Create the documents directory if it doesn't exist
    makedirs(settings.app_docs_dir, exist_ok=True)

    # Get file path
    file_path = join(settings.app_docs_dir, file.filename)

    # Check if the document already exists based on its title or its file path
    doc = get_doc(title=title, file_path=file_path)

    if not doc:
        doc = Document(title=title, file_path=file_path)
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DOC_EXISTS)

    # Save the file to the documents directory
    try:
        file_size = 0

        with open(file_path, "wb") as f:
            while chunk := await file.read(1024):
                file_size += len(chunk)

                if file_size > settings.app_docs_max_size_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=FILE_TOO_LARGE,
                    )

                f.write(chunk)
    except HTTPException:
        # Delete the file if it exists
        if exists(file_path):
            remove(file_path)

        # Re-raise exception
        raise
    except Exception:
        # Delete the file if it exists
        if exists(file_path):
            remove(file_path)

        # Re-raise exception as HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_UPL_DOC.format(doc.title),
        )

    # Process the document in the background
    bg_tasks.add_task(process_doc, doc)

    # Return the document status (Pending)
    return DocumentStatusMessage(document_status=doc.status)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": DOC_DELETED_1},
        status.HTTP_404_NOT_FOUND: {"description": DOC_NOT_FOUND_1},
    },
    response_model=Message,
)
async def delete_document(id: str) -> Message:
    """Delete a document.

    Args:
        id (str): Document ID.

    Raises:
        HTTPException: If the document is not found.

    Returns:
        Message: Success message.
    """
    try:
        # Delete the document
        delete_doc(id)
    except ValueError:
        # Re-raise exception as HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOC_NOT_FOUND_2.format(id),
        )
    except Exception:
        # Re-raise exception as HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_DEL_DOC.format(id),
        )

    return Message(detail=DOC_DELETED_2.format(id))
