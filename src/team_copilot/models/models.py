"""Team Copilot - Models - Models."""

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
    ForeignKey,
    text,
    func,
)

from team_copilot.models.types import VectorType


class Message(SQLModel, table=False):
    """Message model."""

    detail: str


class Token(SQLModel, table=False):
    """Token model."""

    access_token: str
    token_type: str


class TokenData(SQLModel, table=False):
    """Token data model."""

    username: str | None = None


class User(SQLModel, table=False):
    """User model."""

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


class DbUser(User, table=True):
    """Database user model."""

    __tablename__ = "users"
    password_hash: str

    def to_user(self) -> User:
        """Convert the instance to a User instance.

        Returns:
            User: User instance.
        """
        return User(
            id=self.id,
            username=self.username,
            name=self.name,
            email=self.email,
            staff=self.staff,
            admin=self.admin,
            enabled=self.enabled,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


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

    name: str
    path: str

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
