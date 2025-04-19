"""Team Copilot - Models - Data Models."""

from enum import Enum
from uuid import UUID
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint

from sqlalchemy import (
    Column,
    UUID as SA_UUID,
    Text,
    DateTime,
    Enum as SaEnum,
    ForeignKey,
    text,
    func,
)

from team_copilot.models.types import VectorType


class AppStatus(str, Enum):
    """Application status enumeration."""

    AVAILABLE = "available"


class DbStatus(str, Enum):
    """Database status enumeration."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"

    # "id" is a primary key and has a default value generated at the database server, so
    # it requires an explicit Column definition with "sa_column".
    id: UUID | None = Field(
        sa_column=Column(
            SA_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        ),
        default=None,
    )

    username: str = Field(unique=True, min_length=3, max_length=100)
    password_hash: str
    name: str | None = Field(min_length=1, max_length=100, default=None)
    email: str | None = Field(unique=True, min_length=3, max_length=100, default=None)
    staff: bool | None = False
    admin: bool = False
    enabled: bool = False

    # "created_at" and "updated_at" fields have a default value generated at the
    # database server, so they require an explicit Column definition with "sa_column".
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

    # "id" is a primary key and has a default value generated at the database server, so
    # it requires an explicit Column definition with "sa_column".
    id: UUID | None = Field(
        sa_column=Column(
            SA_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        ),
        default=None,
    )

    title: str = Field(unique=True, min_length=1, max_length=100)
    path: str = Field(unique=True, min_length=1, max_length=300)

    # "status" is a custom type, so it requires an explicit Column definition.
    status: DocumentStatus = Field(
        sa_column=Column(
            SaEnum(DocumentStatus, name="document_status"),
            nullable=False,
        ),
        default=DocumentStatus.PENDING,
    )

    # "created_at" and "updated_at" fields have a default value generated at the
    # database server, so they require an explicit Column definition with "sa_column".
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

    # "id" is a primary key and has a default value generated at the database server, so
    # it requires an explicit Column definition with "sa_column".
    id: UUID | None = Field(
        sa_column=Column(
            SA_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        ),
        default=None,
    )

    # "document_id" is a foreign key, so it requires an explicit Column definition with
    # "sa_column".
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
