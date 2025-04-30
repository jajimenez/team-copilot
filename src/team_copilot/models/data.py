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

from passlib.context import CryptContext

from team_copilot.models.types import VectorType


# Messages
PASS_ARG_ERROR = 'Either "password" or "password_hash" must be provided, but not both.'
PASS_VAL_ERROR = "Password must be a string between 8 and 200 characters long."

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    )

    username: str = Field(unique=True, min_length=3, max_length=100)
    password_hash: str
    name: str | None = Field(min_length=1, max_length=100)
    email: str | None = Field(unique=True, min_length=3, max_length=100)
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
    )

    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            server_onupdate=func.now(),
        ),
    )

    # "password" is a property to allow to set the value of the password and set
    # automatically the value of "password_hash" to the hash of the password when the
    # password is set. We don't need the getter method of "property" because we don't
    # want to store the password value in the instance, but we need to define it because
    # it's a requirement of the property decorator.

    @property
    def password(self) -> str:
        """Get the password.

        Raises:
            AttributeError: Always.
        """
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, value: str):
        """Set the password.

        When setting this property, the value isn't actually stored in the instance and
        `password_hash` is set to the hash of the value.

        Args:
            value (str): Password.
        """
        # Validate the password
        self._validate_password(value)

        # Set the password hash
        self.password_hash = pwd_context.hash(value)

    def __init__(self, **kwargs):
        """Initialize the User instance.

        Either "password" or "password_hash" must be provided as a keyword argument, and
        only one of them. If "password" is provided, "password_hash" will be set to the
        hash of "password".

        Args:
            kwargs: Keyword arguments.

        Raises:
            ValueError: If both "password" and "password_hash" are provided or if the
                value of any field is invalid.
        """
        # Make a copy of the keyword arguments dictionary to avoid modifying the original.
        data = kwargs.copy()

        # Check if "password" and "password_hash" are provided in the keyword arguments
        # and raise an exception if none is provided or both are provided.
        if (
            ("password" in data and "password_hash" in data) or
            ("password" not in data and "password_hash" not in data)
        ):
            raise ValueError(PASS_ARG_ERROR)

        if "password" in data:
            # Get the value of "password" from the keyword arguments, which are in the
            # "data" dictionary, and remove it from the dictionary to avoid passing it
            # to the SQLModel initializer as "password" is not a field of the model and
            # passing it to the SQLModel initializer would raise a validation exception.
            password = data.pop("password")

            # Validate the password
            self._validate_password(password)

            # Add "password_hash" to "data" with the hash of "password". We need to
            # include "password_hash" in "data" to pass it to the SQLModel initializer
            # because "password_hash" is a required field of the model and not passing
            # it to the SQLModel initializer would raise a validation exception.
            data["password_hash"] = pwd_context.hash(password)

        # Call the SQLModel initializer, which triggers the validation of the model
        # fields.
        super().__init__(**data)

    def _validate_password(self, value: str):
        """Validate the password.

        The password must be a string between 8 and 200 characters long. If the password
        is invalid, a ValueError is raised.

        Args:
            value (str): Password.

        Raises:
            ValueError: If the password is invalid.
        """
        if not isinstance(value, str) or len(value) < 8 or len(value) > 200:
            raise ValueError(PASS_VAL_ERROR)

    def verify_password(self, password: str) -> bool:
        """Checks if a given password matches the "password" field of this instance.

        The verification is done by comparing the hash of the given password to the
        "password_hash" field of this instance. If they are equal, then the given
        password matches the "password" field of this instance.

        Args:
            password (str): Password to verify.

        Returns:
            bool: Whether the given password matches the "password" field of this
                instance.
        """
        return pwd_context.verify(password, self.password_hash)


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
    )

    name: str = Field(unique=True, min_length=1, max_length=100)

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
    )

    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            server_onupdate=func.now(),
        ),
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
