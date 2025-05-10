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


class AppStatusResponseData(SQLModel, table=False):
    """Application Status Response Data model."""

    status: AppStatus = AppStatus.AVAILABLE

    @classmethod
    def create(cls, status: AppStatus) -> "AppStatusResponseData":
        """Create an AppStatusResponseData instance given a AppStatus instance.

        Returns:
            AppStatusResponseData: AppStatusResponseData instance.
        """
        return cls(status=status)


class AppStatusResponse(MessageResponse):
    """Application Status Response model."""

    data: AppStatusResponseData | None

    @classmethod
    def create(cls, message: str, status: AppStatus) -> "AppStatusResponse":
        """Create an AppStatusResponse instance given a message and an AppStatus
        instance.

        Returns:
            AppStatusResponse: AppStatusResponse instance.
        """
        return cls(message=message, data=AppStatusResponseData.create(status))


class DbStatusResponseData(SQLModel, table=False):
    """Database Status Response model."""

    status: DbStatus

    @classmethod
    def create(cls, status: DbStatus) -> "DbStatusResponseData":
        """Create a DbStatusResponse instance given a DbStatus instance.

        Returns:
            DbStatusResponseData: DbStatusResponseData instance.
        """
        return cls(status=status)


class DbStatusResponse(MessageResponse):
    """Database Status Response model."""

    data: DbStatusResponseData | None

    @classmethod
    def create(cls, message: str, status: DbStatus) -> "DbStatusResponse":
        """Create a DbStatusResponse instance given a message and a DbStatus instance.

        Returns:
            DbStatusResponse: DbStatusResponse instance.
        """
        return cls(message=message, data=DbStatusResponseData.create(status))


class TokenResponse(SQLModel, table=False):
    """Token model."""

    access_token: str
    token_type: str


class UserResponseData(SQLModel, table=False):
    """User Response Data model."""

    id: UUID | None
    username: str
    name: str | None
    email: EmailStr | None
    staff: bool
    admin: bool
    enabled: bool

    @classmethod
    def create(cls, user: User) -> "UserResponseData":
        """Create a UserResponseData instance given a User instance.

        Returns:
            UserResponseData: UserResponseData instance.
        """
        return cls(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            staff=user.staff,
            admin=user.admin,
            enabled=user.enabled,
        )


class UserResponse(MessageResponse):
    """User Response model."""

    data: UserResponseData | None

    @classmethod
    def create(cls, message: str, user: User) -> "UserResponse":
        """Create a UserResponse instance given a message and a User instance.

        Returns:
            UserResponse: UserResponse instance.
        """
        return cls(message=message, data=UserResponseData.create(user))


class UserSavedResponseData(SQLModel, table=False):
    """User Saved Response Data model."""

    id: UUID | None

    @classmethod
    def create(cls, user: User) -> "UserSavedResponseData":
        """Create a UserSavedResponseData instance given a User instance.

        Returns:
            UserSavedResponseData: UserSavedResponseData instance.
        """
        return cls(id=user.id)


class UserSavedResponse(MessageResponse):
    """User Saved response model."""

    data: UserSavedResponseData | None

    @classmethod
    def create(cls, message: str, user: User) -> "UserSavedResponse":
        """Create a UserSavedResponse instance given a message and a User instance.

        Returns:
            UserSavedResponse: UserSavedResponse instance.
        """
        return cls(message=message, data=UserSavedResponseData.create(user))


class DocumentResponseData(SQLModel, table=False):
    """Document Response Data model."""

    id: UUID | None
    name: str
    status: DocumentStatus
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def create(cls, document: Document) -> "DocumentResponseData":
        """Create a DocumentResponseData instance given a Document instance.

        Returns:
            DocumentResponseData: DocumentResponseData instance.
        """
        return cls(
            id=document.id,
            name=document.name,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class DocumentResponse(MessageResponse):
    """Document Response model."""

    data: DocumentResponseData | None

    @classmethod
    def create(cls, message: str, document: Document) -> "DocumentResponse":
        """Create a DocumentResponse instance given a message and a Document instance.

        Returns:
            DocumentResponse: DocumentResponse instance.
        """
        return cls(message=message, data=DocumentResponseData.create(document))


class DocumentStatusResponseData(SQLModel, table=False):
    """Document Status Response Data model."""

    document_id: UUID
    document_status: DocumentStatus

    @classmethod
    def create(cls, document: Document) -> "DocumentStatusResponseData":
        """Create a DocumentStatusResponseData instance given a Document instance.

        Returns:
            DocumentStatusResponseData: DocumentStatusResponseData instance.
        """
        return cls(document_id=document.id, document_status=document.status)


class DocumentStatusResponse(MessageResponse):
    """Document Status Response model."""

    data: DocumentStatusResponseData | None

    @classmethod
    def create(cls, message: str, document: Document) -> "DocumentStatusResponse":
        """Create a DocumentStatusResponse instance given a message and a Document
        instance.

        Returns:
            DocumentStatusResponse: DocumentStatusResponse instance.
        """
        return cls(message=message, data=DocumentStatusResponseData.create(document))


class DocumentListResponse(MessageResponse):
    """Document List Response model."""

    data: list[DocumentResponseData] | None

    @classmethod
    def create(cls, message: str, documents: list[Document]) -> "DocumentListResponse":
        """Create a DocumentListResponse instance given a message and a list of Document
        instances.

        Returns:
            DocumentListResponse: DocumentListResponse instance.
        """
        docs = [DocumentResponseData.create(d) for d in documents]
        return cls(message=message, data=docs)


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
