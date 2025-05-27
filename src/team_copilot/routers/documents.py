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
from team_copilot.models.data import Document, DocumentStatus
from team_copilot.models.request import CreateDocumentRequest, UpdateDocumentRequest

from team_copilot.models.response import (
    Response,
    ErrorResponse,
    DocumentResponse,
    DocumentCreatedResponse,
    DocumentListResponse,
)

from team_copilot.services.documents import (
    get_all_documents as get_all_docs,
    get_document as get_doc,
    get_document_file_path,
    save_document,
    process_document,
    delete_document as del_doc,
)

from team_copilot.routers import BAD_REQ, VAL_ERROR, NOT_AUTHENTICATED, NOT_AUTHORIZED


# Descriptions and messages
max_size_mb = settings.app_docs_max_size_bytes // (1024 * 1024)

CRE_DOC_DESC = "Create a document. Only staff users are authorized."
CRE_DOC_SUM = "Create a document"
DEL_DOC_DESC = "Delete a document. Only staff users are authorized."
DEL_DOC_SUM = "Delete a document"
DOC_ACC = "Document accepted"
DOC_CRE_SCH = "Document {} ({}) created and scheduled for processing."
DOC_DAT = "Document data"
DOC_DEL_1 = "Document deleted"
DOC_DEL_2 = "Document {} ({}) deleted."
DOC_EXISTS_1 = "A document with the same name already exists"
DOC_EXISTS_2 = "A document with the same name already exists."
DOC_FILE = "Document PDF file"
DOC_ID = "Document ID"
DOC_NAME = "Document name"
DOC_NF_1 = "Document not found"
DOC_NF_2 = "Document {} not found."
DOC_RET = "Document {} ({}) retrieved."
DOC_UPD_SCH = "Document {} ({}) updated and scheduled for processing."
DOCS_DAT = "Documents data"
DOCS_RET_1 = "1 document retrieved."
DOCS_RET_2 = "{} documents retrieved."
FILE_TOO_LARGE_1 = f"The file size exceeds the maximum limit ({max_size_mb} MB)"
FILE_TOO_LARGE_2 = f"The file size exceeds the maximum limit ({max_size_mb} MB)."
GET_ALL_DOCS_DESC = "Get all documents. Only staff users are authorized."
GET_ALL_DOCS_SUM = "Get all documents"
GET_DOC_DESC = "Get a document. Only staff users are authorized."
GET_DOC_SUM = "Get a document"
UNS_FILE_TYP_1 = "Unsupported file type (only PDF files are allowed)"
UNS_FILE_TYP_2 = "Unsupported file type (only PDF files are allowed)."
UPD_ARG_ERR = "At least one of the name or file must be provided."

UPD_DOC_DESC = (
    "Update a document (one or both fields). Only staff users are authorized. To update"
    " only one of the fields, omit the other one from the request (don't send it with "
    "an empty value). Note that the OpenAPI UI doesn't support omitting a field when "
    "sending a request with the form-data content type (instead, it sends the field "
    "with an empty value). "
)

UPD_DOC_SUM = "Update a document"

# In the "create_document" and "update_document" endpoints, we can't set a SQLModel as
# the input schema holding both the document name and the document file because SQLModel
# doesn't support file uploads. Also, we can't use a SQLModel to hold just the name
# (e.g. the "team_copilot.models.request.CreateDocumentRequest" model, which contains
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
    "Body_create_document": "CreateDocumentRequest",
    "Body_update_document": "UpdateDocumentRequest",
}

# Requests
DOC_MIME_TYPE = "application/pdf"

# Router
router = APIRouter(
    dependencies=[Depends(get_staff_user)],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": BAD_REQ,
            "model": ErrorResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": NOT_AUTHENTICATED,
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": NOT_AUTHORIZED,
            "model": ErrorResponse,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": VAL_ERROR,
            "model": ErrorResponse,
        },
    },
)


def validate_name(name: str | None, update: bool = False):
    """Validate a document request name.

    Args:
        name (str | None): Document request name.
        update (bool): Whether the request is an update request or not.

    Raises:
        RequestValidationError: If the name is invalid.
    """
    try:
        # If the name is invalid, creating an UpdateDocumentRequest object or a
        # CreateDocumentRequest will raise a ValueError.
        if update:
            UpdateDocumentRequest(name=name)
        else:
            CreateDocumentRequest(name=name)
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
        raise RequestValidationError(UNS_FILE_TYP_2)

    if file.size > settings.app_docs_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=FILE_TOO_LARGE_2,
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
                        detail=FILE_TOO_LARGE_2,
                    )

                f.write(chunk)
    except Exception:
        # Delete the file if it exists
        if exists(path):
            remove(path)

        # Re-raise exception
        raise


@router.get(
    "/",
    operation_id="get_all_documents",
    summary=GET_ALL_DOCS_SUM,
    description=GET_ALL_DOCS_DESC,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": DOCS_DAT,
            "model": DocumentListResponse,
        },
    },
)
async def get_all_documents() -> DocumentListResponse:
    """Get all documents.

    Returns:
        DocumentListResponse: Message, document count and documents.
    """
    # Get all the documents from the database
    docs = get_all_docs()

    # Get document count and message
    count = len(docs)
    message = DOCS_RET_1 if count == 1 else DOCS_RET_2.format(count)

    # Return message, document count and documents.
    return DocumentListResponse.create(message=message, documents=docs)


@router.get(
    "/{id}",
    operation_id="get_document",
    summary=GET_DOC_SUM,
    description=GET_DOC_DESC,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": DOC_DAT,
            "model": DocumentResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NF_1,
            "model": ErrorResponse,
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
        DocumentResponse: Message and document.
    """
    # Get the document from the database
    doc = get_doc(id=id)

    # Check that the document exists
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOC_NF_2.format(id),
        )

    # Return message and document
    message = DOC_RET.format(doc.id, doc.name)
    return DocumentResponse.create(message=message, document=doc)


@router.post(
    "/",
    operation_id="create_document",
    summary=CRE_DOC_SUM,
    description=CRE_DOC_DESC,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": DOC_ACC,
            "model": DocumentCreatedResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": DOC_EXISTS_1,
            "model": ErrorResponse,
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": FILE_TOO_LARGE_1,
            "model": ErrorResponse,
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "description": UNS_FILE_TYP_1,
            "model": ErrorResponse,
        },
    },
)
async def create_document(
    name: Annotated[str, Form(description=DOC_NAME, min_length=1, max_length=100)],
    file: Annotated[UploadFile, File(description=DOC_FILE)],
    bg_tasks: BackgroundTasks,
) -> DocumentCreatedResponse:
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
        DocumentCreatedResponse: Message, document ID and document status.
    """
    # Check that the name is valid
    validate_name(name)

    # Check that the file to upload is valid
    validate_file(file)

    # Check that another document with the same name doesn't exist
    if get_doc(name=name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DOC_EXISTS_2)

    # Create a new Document object (the status is set to "pending" by default)
    doc = Document(name=name)

    # Save the Document object to the database. The ID of the document is set by the
    # database and is set in the Document object by "save_document".
    save_document(doc)

    # Get the path where the PDF file of the document will be saved temporarily
    file_path = get_document_file_path(doc.id)

    # Upload the file
    await upload_file(file, file_path)

    # Process the document in the background. The temporary PDF file of the document is
    # deleted after the processing finishes.
    bg_tasks.add_task(process_document, doc.id)

    # Return message, document ID and document status (which is initially "pending").
    message = DOC_CRE_SCH.format(doc.id, doc.name)
    return DocumentCreatedResponse.create(message=message, document=doc)


@router.put(
    "/{id}",
    operation_id="update_document",
    summary=UPD_DOC_SUM,
    description=UPD_DOC_DESC,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": DOC_ACC,
            "model": DocumentResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NF_1,
            "model": ErrorResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": DOC_EXISTS_1,
            "model": ErrorResponse,
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": FILE_TOO_LARGE_1,
            "model": ErrorResponse,
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "description": UNS_FILE_TYP_1,
            "model": ErrorResponse,
        },
    },
)
async def update_document(
    bg_tasks: BackgroundTasks,
    id: Annotated[UUID, Path(description=DOC_ID)],
    name: Annotated[
        str | None, Form(description=DOC_NAME, min_length=1, max_length=100)
    ] = None,
    file: Annotated[UploadFile | None, File(description=DOC_FILE)] = None,
) -> DocumentResponse:
    """Update a document.

    Args:
        bg_tasks (BackgroundTasks): Background tasks.
        id (UUID): Document ID.
        name (str | None): New document name.
        file (UploadFile | None): New document PDF file.

    Raises:
        RequestValidationError: If no fields are provided or the name is invalid or the
            file type isn't supported.
        HTTPException: If the document doesn't exist or another document with the same
            name exists or the file size exceeds the maximum limit.

    Returns:
        DocumentResponse: Message and document.
    """
    # Check that at least one of the name or file is provided
    if name is None and file is None:
        raise RequestValidationError([UPD_ARG_ERR])

    # Check that the document exists and get the document
    doc = get_doc(id=id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOC_NF_2.format(id),
        )

    # Validate and update name if provided
    if name is not None:
        # Check that the name is valid
        validate_name(name, True)

        # Check that another document with the same name doesn't exist
        other_doc = get_doc(name=name)

        if other_doc and other_doc.id != id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=DOC_EXISTS_2,
            )

        # Update name
        doc.name = name

    # Validate file if provided
    if file is not None:
        # Check that the file to upload is valid
        validate_file(file)

    # Set the "updated_at" field to None to let the database update it to the current
    # timestamp when we save it to the database.
    doc.updated_at = None

    # Set the document status if the file is provided
    if file is not None:
        doc.status = DocumentStatus.PENDING

    # Save the document object to the database
    save_document(doc)

    # Process file if provided
    if file is not None:
        # Get the path where the PDF file of the document will be saved temporarily
        file_path = get_document_file_path(doc.id)

        # Upload the file
        await upload_file(file, file_path)

        # Process the document in the background. The temporary PDF file of the document
        # is deleted after the processing finishes.
        bg_tasks.add_task(process_document, doc.id)

    # Return message and document
    message = DOC_UPD_SCH.format(doc.id, doc.name)
    return DocumentResponse.create(message=message, document=doc)


@router.delete(
    "/{id}",
    operation_id="delete_document",
    summary=DEL_DOC_SUM,
    description=DEL_DOC_DESC,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": DOC_DEL_1,
            "model": Response,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": DOC_NF_1,
            "model": ErrorResponse,
        },
    },
)
async def delete_document(id: Annotated[UUID, Path(description=DOC_ID)]) -> Response:
    """Delete a document.

    Args:
        id (UUID): Document ID.

    Raises:
        HTTPException: If the document is not found.

    Returns:
        Response: Message.
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
        del_doc(id)
    except ValueError:
        # Re-raise exception as HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOC_NF_2.format(id),
        )

    # Return message
    return Response(message=DOC_DEL_2.format(id, name))
