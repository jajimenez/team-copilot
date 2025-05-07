"""Team Copilot - Models - Response Models."""

from uuid import UUID
from datetime import datetime
import json

from sqlmodel import SQLModel
from pydantic import EmailStr

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

    id: UUID
    username: str
    name: str | None
    email: EmailStr | None
    staff: bool
    admin: bool
    enabled: bool
    created_at: datetime
    updated_at: datetime

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


class UserSavedResponse(MessageResponse):
    """User saved response model."""

    user_id: UUID


class DocumentResponse(SQLModel, table=False):
    """Document Response model."""

    id: UUID | None
    name: str
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
            name=document.name,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class DocumentStatusResponse(SQLModel, table=False):
    """Document status response model."""

    document_id: UUID
    document_status: DocumentStatus


class AgentResponseChunk(SQLModel, table=False):
    """Agent response chunk model."""

    index: int
    last: bool = False
    text: str

    def to_sse(self) -> str:
        """Convert the instance to an event string with the Server-Sent Events (SSE)
        format.

        Returns:
            str: Server-Sent Events (SSE) event string, containing "data: " followed by
                the actual data in JSON format ({"index": string, "last": boolean,
                "text": string}) and followed by two newline characters.
        """
        # We call the "json.dumps" function and the "SQLModel.model_dump" method instead
        # of calling the "SQLModel.model_dump_json" method directly because
        # "SQLModel.model_dump_json" generates the JSON string without a whitespace
        # after each separator (comma or semicolon) and it doesn't allow to add the
        # whitespaces.
        data = json.dumps(self.model_dump(), separators=(", ", ": "))
        return f"data: {data}\n\n"
