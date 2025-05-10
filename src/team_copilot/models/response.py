"""Team Copilot - Models - Response Models."""

from uuid import UUID
from datetime import datetime
import json

from sqlmodel import SQLModel
from pydantic import EmailStr

from team_copilot.models.data import AppStatus, DbStatus, DocumentStatus, User, Document


class Response(SQLModel, table=False):
    """Response model."""

    message: str


class ErrorResponseData(SQLModel, table=False):
    """Error Response Data model."""

    error: str


class ErrorResponse(Response):
    """Error Response model."""

    data: ErrorResponseData | None

    @classmethod
    def create(cls, message: str, error: str) -> "ErrorResponse":
        """Create an ErrorResponse instance given a message and an error string.

        Returns:
            ErrorResponse: ErrorResponse instance.
        """
        return cls(message=message, data=ErrorResponseData(error=error))


class AppStatusResponseData(SQLModel, table=False):
    """Application Status Response Data model."""

    status: AppStatus = AppStatus.AVAILABLE


class AppStatusResponse(Response):
    """Application Status Response model."""

    data: AppStatusResponseData | None

    @classmethod
    def create(cls, message: str, status: AppStatus) -> "AppStatusResponse":
        """Create an AppStatusResponse instance given a message and an AppStatus
        instance.

        Returns:
            AppStatusResponse: AppStatusResponse instance.
        """
        return cls(message=message, data=AppStatusResponseData(status=status))


class DbStatusResponseData(SQLModel, table=False):
    """Database Status Response model."""

    status: DbStatus


class DbStatusResponse(Response):
    """Database Status Response model."""

    data: DbStatusResponseData | None

    @classmethod
    def create(cls, message: str, status: DbStatus) -> "DbStatusResponse":
        """Create a DbStatusResponse instance given a message and a DbStatus instance.

        Returns:
            DbStatusResponse: DbStatusResponse instance.
        """
        return cls(message=message, data=DbStatusResponseData(status=status))


class TokenResponse(SQLModel, table=False):
    """Token Response model."""

    access_token: str
    token_type: str = "bearer"


class UserResponseData(SQLModel, table=False):
    """User Response Data model."""

    id: UUID | None
    username: str
    name: str | None
    email: EmailStr | None
    staff: bool
    admin: bool
    enabled: bool
    created_at: datetime
    updated_at: datetime

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
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserResponse(Response):
    """User Response model."""

    data: UserResponseData | None

    @classmethod
    def create(cls, message: str, user: User) -> "UserResponse":
        """Create a UserResponse instance given a message and a User instance.

        Returns:
            UserResponse: UserResponse instance.
        """
        return cls(message=message, data=UserResponseData.create(user))


class UserCreatedResponseData(SQLModel, table=False):
    """User Created Response Data model."""

    user_id: UUID | None

    @classmethod
    def create(cls, user: User) -> "UserCreatedResponseData":
        """Create a UserCreatedResponseData instance given a User instance.

        Returns:
            UserCreatedResponseData: UserCreatedResponseData instance.
        """
        return cls(user_id=user.id)


class UserCreatedResponse(Response):
    """User Created response model."""

    data: UserCreatedResponseData | None

    @classmethod
    def create(cls, message: str, user: User) -> "UserCreatedResponse":
        """Create a UserCreatedResponse instance given a message and a User instance.

        Returns:
            UserCreatedResponse: UserCreatedResponse instance.
        """
        return cls(message=message, data=UserCreatedResponseData.create(user))


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


class DocumentResponse(Response):
    """Document Response model."""

    data: DocumentResponseData | None

    @classmethod
    def create(cls, message: str, document: Document) -> "DocumentResponse":
        """Create a DocumentResponse instance given a message and a Document instance.

        Returns:
            DocumentResponse: DocumentResponse instance.
        """
        return cls(message=message, data=DocumentResponseData.create(document))


class DocumentCreatedResponseData(SQLModel, table=False):
    """Document Created Response Data model."""

    document_id: UUID
    document_status: DocumentStatus

    @classmethod
    def create(cls, document: Document) -> "DocumentCreatedResponseData":
        """Create a DocumentCreatedResponseData instance given a Document instance.

        Returns:
            DocumentCreatedResponseData: DocumentCreatedResponseData instance.
        """
        return cls(document_id=document.id, document_status=document.status)


class DocumentCreatedResponse(Response):
    """Document Created Response model."""

    data: DocumentCreatedResponseData | None

    @classmethod
    def create(cls, message: str, document: Document) -> "DocumentCreatedResponse":
        """Create a DocumentCreatedResponse instance given a message and a Document
        instance.

        Returns:
            DocumentCreatedResponse: DocumentCreatedResponse instance.
        """
        return cls(message=message, data=DocumentCreatedResponseData.create(document))


class DocumentListResponse(Response):
    """Document List Response model."""

    count: int
    data: list[DocumentResponseData] | None

    @classmethod
    def create(cls, message: str, documents: list[Document]) -> "DocumentListResponse":
        """Create a DocumentListResponse instance given a message and a list of Document
        instances.

        Returns:
            DocumentListResponse: DocumentListResponse instance.
        """
        docs = [DocumentResponseData.create(d) for d in documents]
        return cls(count=len(docs), message=message, data=docs)


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
