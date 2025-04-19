"""Team Copilot - Routers - Documents."""

from os import makedirs, remove
from os.path import join, exists
from uuid import UUID
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    BackgroundTasks,
    status,
)

from fastapi.exceptions import RequestValidationError, HTTPException

from team_copilot.core.config import Settings, get_settings, settings
from team_copilot.models.data import Document
from team_copilot.models.request import DocumentRequest

from team_copilot.models.response import (
    MessageResponse,
    DocumentResponse,
    DocumentStatusResponse,
)

from team_copilot.dependencies import get_staff_user
from team_copilot.services.documents import save_doc, get_doc, process_doc, delete_doc
from team_copilot.routers import VALIDATION_ERROR, UNAUTHORIZED


# Messages
max_size_mb = settings.app_docs_max_size_bytes // (1024 * 1024)

DOC_DATA = "Document data."
DOC_ACCEPTED = "Document accepted."
NO_FILE_NAME = "The file does not have a name."
UNSUPPORTED_FILE_TYPE = "Unsupported file type (only PDF files are allowed)."
DOC_EXISTS = "A document with the same title or file name already exists."
FILE_TOO_LARGE = f"The file size exceeds the maximum limit ({max_size_mb} MB)."
ERROR_UPL_FILE = 'Error uploading file "{}".'
DOC_DELETED_1 = "Document deleted."
DOC_DELETED_2 = 'Document "{}" deleted.'
DOC_NOT_FOUND_1 = "Document not found."
DOC_NOT_FOUND_2 = 'Document "{}" not found.'
ERROR_DEL_DOC = 'Error deleting document "{}".'

# API documentation
GET_DOC_DESC = "Get a document."
CREATE_DOC_DESC = "Create a document."
UPDATE_DOC_DESC = "Update a document."
DELETE_DOC_DESC = "Delete a document."

# Files
DOC_MIME_TYPE = "application/pdf"

# Router
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_staff_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": UNAUTHORIZED,
            "model": MessageResponse,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": VALIDATION_ERROR,
            "model": MessageResponse,
        },
    },
)


def validate_title(title: str):
    """Validate a document title.

    Args:
        title (str): Document title.

    Raises:
        RequestValidationError: If the title is invalid.
    """
    try:
        # If the title is invalid, creating a document will raise a ValueError
        DocumentRequest(title=title)
    except ValueError as e:
        # Re-raise the exception as a RequestValidationError exception, which will be
        # caught by an exception handler in the "team_copilot.main" module.
        raise RequestValidationError(e.errors())


def validate_file(file: UploadFile):
    """Validate a document PDF file.

    Args:
        file (UploadFile): Document PDF file.

    Raises:
        RequestValidationError: If the file type is not supported or the file name is
            missing.
    """
    # Any RequestValidationError raised will be caught by an exception handler in the
    # "team_copilot.main" module.

    # Validate that the file has a name
    if not file.filename:
        raise RequestValidationError(NO_FILE_NAME)

    # Validate file type
    if file.content_type != DOC_MIME_TYPE:
        raise RequestValidationError(UNSUPPORTED_FILE_TYPE)


async def upload_file(file: UploadFile, path: str):
    """Upload a file.

    Args:
        file (UploadFile): PDF file.
        path (str): Path to save the file.

    Raises:
        HTTPException: If the file size exceeds the maximum limit.
    """
    try:
        file_size = 0

        with open(path, "wb") as f:
            while chunk := await file.read(1024):
                file_size += len(chunk)

                if file_size > settings.app_docs_max_size_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=FILE_TOO_LARGE,
                    )

                f.write(chunk)
    except Exception:
        # Delete the file if it exists
        if exists(path):
            remove(path)

        # Re-raise exception
        raise


@router.get(
    "/{id}",
    description=GET_DOC_DESC,
    responses={
        status.HTTP_200_OK: {
            "description": DOC_DATA,
            "model": DocumentResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NOT_FOUND_1,
            "model": MessageResponse,
        },
    },
)
async def get_document(id: UUID) -> DocumentResponse:
    """Get a document.

    Args:
        id (UUID): Document ID.

    Raises:
        HTTPException: If the document is not found.

    Returns:
        DocumentResponse: Document response.
    """
    # Get the document from the database
    doc = get_doc(id=id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOC_NOT_FOUND_2.format(id),
        )

    return DocumentResponse.from_document(doc)


@router.post(
    "/",
    description=CREATE_DOC_DESC,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": DOC_ACCEPTED,
            "model": DocumentStatusResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": DOC_EXISTS,
            "model": MessageResponse,
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": FILE_TOO_LARGE,
            "model": MessageResponse,
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "description": UNSUPPORTED_FILE_TYPE,
            "model": MessageResponse,
        },
    },
)
async def create_document(
    title: str,
    file: Annotated[UploadFile, File(description="PDF file to upload")],
    bg_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentStatusResponse:
    """Create a document.

    Args:
        title (str): Document title.
        file (UploadFile): Document PDF file.
        bg_tasks (BackgroundTasks): Background tasks.
        settings (Settings): Application settings.
        response (Response): Response.

    Raises:
        HTTPException: If the file type is not supported or the file name is missing.

    Returns:
        DocumentStatus: Document status.
    """
    # Check that the title is valid
    validate_title(title)

    # Check that the file to upload is valid
    validate_file(file)

    # Get file path
    path = join(settings.app_docs_dir, file.filename)

    # Check if the document already exists based on its title or its file path
    if get_doc(title=title, path=path):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DOC_EXISTS)

    # Create a new document object
    doc = Document(title=title, path=path)

    # Save the document object to the database. The ID of the document is set by the
    # database and it's set in the document object by "save_doc".
    save_doc(doc)

    # Create the documents directory if it doesn't exist
    makedirs(settings.app_docs_dir, exist_ok=True)

    # Upload the file and save it to the documents directory
    await upload_file(file, path)

    # Process the document in the background
    bg_tasks.add_task(process_doc, doc.id)

    # Return the document status
    return DocumentStatusResponse(document_id=doc.id, document_status=doc.status)


@router.put(
    "/{id}",
    description=UPDATE_DOC_DESC,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": DOC_ACCEPTED,
            "model": DocumentStatusResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NOT_FOUND_1,
            "model": MessageResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": DOC_EXISTS,
            "model": MessageResponse,
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": FILE_TOO_LARGE,
            "model": MessageResponse,
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "description": UNSUPPORTED_FILE_TYPE,
            "model": MessageResponse,
        },
    },
)
async def update_document(
    id: UUID,
    title: str,
    file: Annotated[UploadFile, File(description="PDF file to upload")],
    bg_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentStatusResponse:
    """Update a document.

    Args:
        id (UUID): Document ID.
        title (str): New document title.
        file (UploadFile): New document PDF file.
        bg_tasks (BackgroundTasks): Background tasks.
        settings (Settings): Application settings.

    Raises:
        HTTPException: If the file type is not supported or the file name is missing or
            the document is not found.

    Returns:
        DocumentStatus: Document status.
    """
    # Check that the title is valid
    validate_title(title)

    # Check that the file to upload is valid
    validate_file(file)

    # Get file path
    path = join(settings.app_docs_dir, file.filename)

    # Check that the document exists
    doc = get_doc(id=id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOC_NOT_FOUND_2.format(id),
        )

    # Check if another document with the same title or file path already exists
    other_doc = get_doc(title=title, path=path)

    if other_doc and str(other_doc.id) != id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DOC_EXISTS)

    # Update the document object. We set the "updated_at" field to None to let the
    # database set it to the current timestamp when we save it to the database.
    doc.title = title
    doc.path = path
    doc.updated_at = None

    # Save the document object to the database
    save_doc(doc)

    # Create the documents directory if it doesn't exist
    makedirs(settings.app_docs_dir, exist_ok=True)

    # Upload the file and save it to the documents directory
    await upload_file(file, path)

    # Process the document in the background
    bg_tasks.add_task(process_doc, doc.id)

    # Return the document status
    return DocumentStatusResponse(document_id=doc.id, document_status=doc.status)


@router.delete(
    "/{id}",
    description=DELETE_DOC_DESC,
    responses={
        status.HTTP_200_OK: {
            "description": DOC_DELETED_1,
            "model": MessageResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NOT_FOUND_1,
            "model": MessageResponse,
        },
    },
)
async def delete_document(id: UUID) -> MessageResponse:
    """Delete a document.

    Args:
        id (UUID): Document ID.

    Raises:
        HTTPException: If the document is not found.

    Returns:
        MessageResponse: Success message.
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

    return MessageResponse(message=DOC_DELETED_2.format(id))
