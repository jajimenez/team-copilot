"""Team Copilot - Routers - Documents."""

from os import makedirs, remove
from os.path import exists, dirname
from uuid import UUID
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Form,
    File,
    UploadFile,
    BackgroundTasks,
    status,
)

from fastapi.exceptions import RequestValidationError, HTTPException

from team_copilot.core.config import settings
from team_copilot.core.auth import get_staff_user
from team_copilot.models.data import Document
from team_copilot.models.request import DocumentRequest

from team_copilot.models.response import (
    MessageResponse,
    DocumentResponse,
    DocumentStatusResponse,
)

from team_copilot.services.documents import (
    get_doc_temp_file_path,
    save_doc,
    get_doc,
    process_doc,
    delete_doc,
)

from team_copilot.routers import VAL_ERROR, UNAUTH


# Descriptions and messages
max_size_mb = settings.app_docs_max_size_bytes // (1024 * 1024)

CRE_DOC_DESC = "Create a document. Only staff users are authorized."
CRE_DOC_SUM = "Create a document"
DEL_DOC_DESC = "Delete a document. Only staff users are authorized."
DEL_DOC_SUM = "Delete a document"
DOC_ACC = "Document accepted."
DOC_DATA = "Document data."
DOC_DEL_1 = "Document deleted."
DOC_DEL_2 = "Document {} ({}) deleted."
DOC_EXISTS = "A document with the same name exists."
DOC_FILE = "Document PDF file."
DOC_ID = "Document ID."
DOC_NF_1 = "Document not found."
DOC_NF_2 = "Document {} not found."
DOC_NAME = "Document name."
ERROR_DEL_DOC = "Error deleting document {}."
ERROR_UPL_FILE = "Error uploading file {}."
FILE_TOO_LARGE = f"The file size exceeds the maximum limit ({max_size_mb} MB)."
GET_DOC_DESC = "Get a document."
GET_DOC_SUM = "Get a document"
UNSUPPORTED_FILE_TYPE = "Unsupported file type (only PDF files are allowed)."
UPD_DOC_DESC = "Update a document. Only staff users are authorized."
UPD_DOC_SUM = "Update a document"

# In the "create_document" and "update_document" endpoints, we can't set a SQLModel as
# the input schema holding both the document name and the document file because SQLModel
# doesn't support file uploads. Also, we can't use a SQLModel to hold just the name
# (e.g. the "team_copilot.models.request.DocumentRequest" model, which contains
# only the name), because SQLModel works with JSON strings and the file is sent as
# "multipart/form-data", which would make the request body an invalid JSON string.
# Therefore, we need to send the name as "multipart/form-data" as well, using the "Form"
# class and use the "DocumentRequest" model to validate the name.

# By not using a SQLModel model as the input schema of the "create_document" and
# "update_document" endpoints, the FastAPI application object generates schema names
# equal to the operation IDs of the endpoints. Therefore, we need to rename the schemas
# in the OpenAPI documentation that the FastAPI application object generates (see the
# "team_copilot.main" module).

# Schemas to rename
SCHEMA_NAMES = {
    "Body_create_document": "DocumentRequest",
    "Body_update_document": "DocumentRequest",
}

# Requests
DOC_MIME_TYPE = "application/pdf"

# Router
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_staff_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": UNAUTH,
            "model": MessageResponse,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": VAL_ERROR,
            "model": MessageResponse,
        },
    },
)


def validate_name(name: str):
    """Validate a document request name.

    Args:
        name (str): Document request name.

    Raises:
        RequestValidationError: If the name is invalid.
    """
    try:
        # If the name is invalid, creating a DocumentRequest object will raise a
        # ValueError.
        DocumentRequest(name=name)
    except ValueError as e:
        # Re-raise the exception as a RequestValidationError exception, which will be
        # caught by one of the exception handlers in the "team_copilot.main" module.
        raise RequestValidationError(e.errors())


def validate_file(file: UploadFile):
    """Validate a document PDF file.

    Args:
        file (UploadFile): Document PDF file.

    Raises:
        RequestValidationError: If the file type isn't supported.
        HTTPException: If the file size exceeds the maximum limit.
    """
    # Any exception raised will be caught by one of the exception handlers in the
    # "team_copilot.main" module.

    # Validate file type
    if file.content_type != DOC_MIME_TYPE:
        raise RequestValidationError(UNSUPPORTED_FILE_TYPE)

    if file.size > settings.app_docs_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=FILE_TOO_LARGE,
        )


async def upload_file(file: UploadFile, path: str):
    """Upload a file.

    Args:
        file (UploadFile): PDF file.
        path (str): Path to save the file.

    Raises:
        HTTPException: If the file size exceeds the maximum limit.
    """
    try:
        # Create the directory of the file if it doesn't exist
        dir_path = dirname(path)
        makedirs(dir_path, exist_ok=True)

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
    operation_id="get_document",
    summary=GET_DOC_SUM,
    description=GET_DOC_DESC,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": DOC_DATA,
            "model": DocumentResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NF_1,
            "model": MessageResponse,
        },
    },
)
async def get_document(
    id: Annotated[UUID, Path(description=DOC_ID)],
) -> DocumentResponse:
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
            detail=DOC_NF_2.format(id),
        )

    return DocumentResponse.from_document(doc)


@router.post(
    "/",
    operation_id="create_document",
    summary=CRE_DOC_SUM,
    description=CRE_DOC_DESC,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": DOC_ACC,
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
    name: Annotated[str, Form(description=DOC_NAME, min_length=1, max_length=100)],
    file: Annotated[UploadFile, File(description=DOC_FILE)],
    bg_tasks: BackgroundTasks,
) -> DocumentStatusResponse:
    """Create a document.

    Args:
        name (str): Document name.
        file (UploadFile): Document PDF file.
        bg_tasks (BackgroundTasks): Background tasks.

    Raises:
        RequestValidationError: If the name is invalid or the file type isn't supported.
        HTTPException: If another document with the same name exists or the file size
            exceeds the maximum limit.

    Returns:
        DocumentStatus: Document ID and status.
    """
    # Check that the name is valid
    validate_name(name)

    # Check that the file to upload is valid
    validate_file(file)

    # Check that another document with the same name doesn't exist
    if get_doc(name=name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DOC_EXISTS)

    # Create a new Document object
    doc = Document(name=name)

    # Save the Document object to the database. The ID of the document is set by the
    # database and is set in the Document object by "save_doc".
    save_doc(doc)

    # Get the path where the PDF file of the document will be saved temporarily
    file_path = get_doc_temp_file_path(doc.id)

    # Upload the file
    await upload_file(file, file_path)

    # Process the document in the background. The temporary PDF file of the document is
    # deleted after the processing finishes.
    bg_tasks.add_task(process_doc, doc.id)

    # Return the document status, which is initially "Pending".
    return DocumentStatusResponse(document_id=doc.id, document_status=doc.status)


@router.put(
    "/{id}",
    operation_id="update_document",
    summary=UPD_DOC_SUM,
    description=UPD_DOC_DESC,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": DOC_ACC,
            "model": DocumentStatusResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NF_1,
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
    id: Annotated[UUID, Path(description=DOC_ID)],
    name: Annotated[str, Form(description=DOC_NAME, min_length=1, max_length=100)],
    file: Annotated[UploadFile, File(description=DOC_FILE)],
    bg_tasks: BackgroundTasks,
) -> DocumentStatusResponse:
    """Update a document.

    Args:
        id (UUID): Document ID.
        name (str): New document name.
        file (UploadFile): New document PDF file.
        bg_tasks (BackgroundTasks): Background tasks.

    Raises:
        RequestValidationError: If the name is invalid or the file type isn't supported.
        HTTPException: If the document doesn't exist or another document with the same
            name exists or the file size exceeds the maximum limit.

    Returns:
        DocumentStatus: Document ID and status.
    """
    # Check that the name is valid
    validate_name(name)

    # Check that the file to upload is valid
    validate_file(file)

    # Check that the document exists
    doc = get_doc(id=id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOC_NF_2.format(id),
        )

    # Check that another document with the same name doesn't exist
    other_doc = get_doc(name=name)

    if other_doc and other_doc.id != id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DOC_EXISTS)

    # Update the Document object. We set the "updated_at" field to None to let the
    # database set it to the current timestamp when we save it to the database.
    doc.name = name
    doc.updated_at = None

    # Save the Document object to the database
    save_doc(doc)

    # Get the path where the PDF file of the document will be saved temporarily
    file_path = get_doc_temp_file_path(doc.id)

    # Upload the file
    await upload_file(file, file_path)

    # Process the document in the background. The temporary PDF file of the document is
    # deleted after the processing finishes.
    bg_tasks.add_task(process_doc, doc.id)

    # Return the document status
    return DocumentStatusResponse(document_id=doc.id, document_status=doc.status)


@router.delete(
    "/{id}",
    operation_id="delete_document",
    summary=DEL_DOC_SUM,
    description=DEL_DOC_DESC,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": DOC_DEL_1,
            "model": MessageResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NF_1,
            "model": MessageResponse,
        },
    },
)
async def delete_document(
    id: Annotated[UUID, Path(description=DOC_ID)],
) -> MessageResponse:
    """Delete a document.

    Args:
        id (UUID): Document ID.

    Raises:
        HTTPException: If the document is not found.

    Returns:
        MessageResponse: Document ID and a message.
    """
    try:
        # Get the document from the database
        doc = get_doc(id=id)

        # Check that the document exists
        if not doc:
            raise ValueError()

        name = doc.name

        # Delete the document. A ValueError will be raised if the document doesn't
        # exist, although this should never happen because we already checked that the
        # document exists.
        delete_doc(id)
    except ValueError:
        # Re-raise exception as HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOC_NF_2.format(id),
        )

    return MessageResponse(message=DOC_DEL_2.format(id, name))
