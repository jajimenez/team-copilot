"""Team Copilot - Routers - Documents."""

from os import makedirs, remove
from os.path import join, exists
from uuid import uuid4
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    BackgroundTasks,
    Response,
    status,
    HTTPException,
)

from team_copilot.models.models import DocumentStatusResponse, DocumentStatus
from team_copilot.dependencies import get_staff_user
from team_copilot.services.documents import process_doc
from team_copilot.core.config import Settings, get_settings, settings
from team_copilot.routers import UNAUTHORIZED, DOCUMENT_ACCEPTED


# Files
DOC_MIME_TYPE = "application/pdf"

# Messages
max_size_mb = settings.app_docs_max_size_bytes // (1024 * 1024)

FILE_NAME_REQUIRED = "The file name is required"
UNSUPPORTED_FILE_TYPE = "Unsupported file type (only PDF files are allowed)"
FILE_TOO_LARGE = f"The file size exceeds the maximum limit ({max_size_mb} MB)"

# Router
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_staff_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": UNAUTHORIZED}},
)


@router.post(
    "/upload",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {"description": DOCUMENT_ACCEPTED},
        status.HTTP_400_BAD_REQUEST: {"description": FILE_NAME_REQUIRED},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"description": UNSUPPORTED_FILE_TYPE},
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {"description": FILE_TOO_LARGE},
    },
    response_model=DocumentStatusResponse,
)
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF file to upload")],
    bg_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentStatusResponse:
    """Upload a PDF file.

    Args:
        file (UploadFile): PDF file to upload.
        bg_tasks (BackgroundTasks): Background tasks.
        settings (Settings): Application settings.
        response (Response): Response.

    Raises:
        HTTPException: If the file type is not supported or the file name is missing.

    Returns:
        DocumentStatusResponse: Document status.
    """
    # Check that the file has a name
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=FILE_NAME_REQUIRED,
        )

    # Validate file type
    if file.content_type != DOC_MIME_TYPE:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=UNSUPPORTED_FILE_TYPE,
        )

    # Create the documents directory if it doesn't exist
    makedirs(settings.app_docs_dir, exist_ok=True)

    # Generate a unique document ID and the file path
    doc_id = uuid4()
    file_path = join(settings.app_docs_dir, f"{doc_id}_{file.filename}")

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
    except Exception:
        # Delete the file if it exists
        if exists(file_path):
            remove(file_path)

        # Re-raise the exception
        raise

    # Process the document in the background
    bg_tasks.add_task(process_doc, doc_id, file.filename, file_path)

    # Return the document status response
    return DocumentStatusResponse(
        document_id=doc_id,
        document_name=file.filename,
        status = DocumentStatus.PENDING,
    )
