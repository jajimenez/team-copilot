"""Team Copilot - Models - Response Models."""

from os.path import basename
from uuid import UUID
from datetime import datetime

from sqlmodel import SQLModel

from team_copilot.models.data import AppStatus, DbStatus, DocumentStatus, User, Document


class MessageResponse(SQLModel, table=False):
    """Message response model."""

    message: str


class ErrorResponse(SQLModel, table=False):
    """Error response model."""

    error: str


class AppStatusResponse(SQLModel, table=False):
    """Application status response model."""

    status: AppStatus = AppStatus.AVAILABLE


class DbStatusResponse(SQLModel, table=False):
    """Database status response model."""

    status: DbStatus


class TokenResponse(SQLModel, table=False):
    """Token model."""
    
    access_token: str
    token_type: str


class UserResponse(SQLModel, table=False):
    """User Response model."""

    id: UUID | None
    username: str
    name: str | None
    email: str | None
    staff: bool
    admin: bool
    enabled: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        """Convert the instance to a UserResponse instance.

        Returns:
            UserResponse: UserResponse instance.
        """
        return cls(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            staff=user.staff,
            admin=user.admin,
            enabled=user.enabled,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class DocumentResponse(SQLModel, table=False):
    """Document Response model."""

    id: UUID | None
    title: str
    file_name: str
    status: DocumentStatus
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_document(cls, document: Document) -> "DocumentResponse":
        """Convert the instance to a DocumentResponse instance.

        Returns:
            DocumentResponse: DocumentResponse instance.
        """
        return cls(
            id=document.id,
            title=document.title,
            file_name=basename(document.path),
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class DocumentStatusResponse(SQLModel, table=False):
    """Document status response model."""

    document_id: UUID
    document_status: DocumentStatus
