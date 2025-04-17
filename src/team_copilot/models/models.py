"""Team Copilot - Models - Models."""

from os.path import basename
from enum import Enum
from uuid import UUID
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint

from sqlalchemy import (
    Column,
    UUID as SA_UUID,
    String,
    Text,
    Boolean,
    DateTime,
    Enum as SaEnum,
    ForeignKey,
    text,
    func,
)

from team_copilot.models.types import VectorType


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"

    # All the fields except "username" and "name" have a default value generated at the
    # server, so they require an explicit Column definition with "sa_column".

    id: UUID | None = Field(
        sa_column=Column(
            SA_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        ),
        default=None,
    )

    username: str = Field(unique=True)
    password_hash: str
    name: str | None = None

    email: str | None = Field(
        sa_column=Column(
            String,
            unique=True,
            nullable=True,
        ),
        default=None,
    )

    staff: bool = Field(
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default="false",
        ),
        default=False,
    )

    admin: bool = Field(
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default="false",
        ),
        default=False,
    )

    enabled: bool = Field(
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default="false",
        ),
        default=False,
    )

    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        default=None,
    )

    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            server_onupdate=func.now(),
        ),
        default=None,
    )


class DocumentStatus(str, Enum):
    """Document status enumeration."""

    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(SQLModel, table=True):
    """Document model."""

    __tablename__ = "documents"

    # "id", "created_at" and "updated_at" are fields with a default value generated at
    # the server, so they require an explicit Column definition with "sa_column".

    id: UUID | None = Field(
        sa_column=Column(
            SA_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        ),
        default=None,
    )

    title: str = Field(unique=True)
    path: str = Field(unique=True)

    status: DocumentStatus = Field(
        sa_column=Column(
            SaEnum(DocumentStatus, name="document_status"),
            nullable=False,
        ),
        default=DocumentStatus.PENDING,
    )

    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        default=None,
    )

    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            server_onupdate=func.now(),
        ),
        default=None,
    )

    chunks: list["DocumentChunk"] = Relationship(
        back_populates="document",
        sa_relationship_kwargs={"cascade": "all"},
    )


class DocumentChunk(SQLModel, table=True):
    """Document chunk model."""

    __tablename__ = "document_chunks"

    # "id" and "document_id" are fields with a default value generated at the server, so
    # they require an explicit Column definition with "sa_column".

    id: UUID | None = Field(
        sa_column=Column(
            SA_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        ),
        default=None,
    )

    document_id: UUID = Field(
        sa_column=Column(
            SA_UUID(as_uuid=True),
            ForeignKey("documents.id", ondelete="cascade"),
            nullable=False,
        )
    )

    chunk_index: int

    # "chunk_text" is large text so it should be created in SQL as TEXT (not VARCHAR),
    # so it requires an explicit Column definition with "sa_column". Fields without an
    # explicit Column definition are created as VARCHAR by default.
    chunk_text: str = Field(sa_column=Column(Text, nullable=False))

    # "embedding" is a custom type, so it requires an explicit Column definition.
    embedding: list[float] = Field(sa_column=Column(VectorType, nullable=False))

    # Relationships
    document: Document = Relationship(back_populates="chunks")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="unique_document_chunk",
        ),
    )


class AppStatus(str, Enum):
    """Application status enumeration."""

    AVAILABLE = "available"


class DbStatus(str, Enum):
    """Database status enumeration."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class TokenData(SQLModel, table=False):
    """Token data model."""

    username: str | None = None


class MessageResponse(SQLModel, table=False):
    """Message response model."""

    detail: str


class AppStatusResponse(SQLModel, table=False):
    """Application status response model."""

    status: AppStatus = AppStatus.AVAILABLE


class DbStatusResponse(SQLModel, table=False):
    """Database status response model."""

    status: DbStatus


class DocumentStatusResponse(SQLModel, table=False):
    """Document status response model."""

    status: DocumentStatus


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
    title: str = Field(unique=True)
    file_name: str = Field(unique=True)
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
