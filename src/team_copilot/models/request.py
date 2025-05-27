"""Team Copilot - Models - Request Models."""

from pydantic import field_validator, EmailStr
from sqlmodel import SQLModel, Field

from team_copilot.models.data import User


# Descriptions and messages
DOC_NAME = "Document name"
NAME_NOT_EMP = "Name must not be empty."
PASSWORD = "Password"
QUERY_TEXT = "Query text"
USERNAME = "Username"


class Undefined:
    """Class to indicate that a field was not provided in a request.

    This class is used to differentiate between a field that was not provided and a
    field that was provided with a value of None.
    """

    pass


class CreateUserRequest(SQLModel, table=False):
    """Create User Request model."""

    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=200)
    name: str | None = Field(min_length=1, max_length=100)
    email: EmailStr | None = Field(max_length=100)
    staff: bool = False
    admin: bool = False
    enabled: bool = False

    def to_user(self) -> User:
        """Convert the instance to a User instance.

        Returns:
            User: User instance.
        """
        return User(
            username=self.username,
            name=self.name,
            email=self.email,
            password=self.password,
            staff=self.staff,
            admin=self.admin,
            enabled=self.enabled,
        )


class UpdateUserRequest(SQLModel, table=False):
    """Update User Request model."""

    username: str = Field(default=Undefined, min_length=3, max_length=100)
    password: str = Field(default=Undefined, min_length=8, max_length=200)
    name: str | None = Field(default=Undefined, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=Undefined, max_length=100)
    staff: bool = Field(default=Undefined)
    admin: bool = Field(default=Undefined)
    enabled: bool = Field(default=Undefined)


class CreateDocumentRequest(SQLModel, table=False):
    """Create Document Request model."""

    name: str = Field(min_length=1, max_length=100, description=DOC_NAME)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate the name field.

        The name field, when stripped, must not be empty.

        Args:
            v (str): Name value.

        Raises:
            ValueError: If the name is invalid.

        Returns:
            str: Name value.
        """
        if not v.strip():
            raise ValueError(NAME_NOT_EMP)

        return v


class UpdateDocumentRequest(SQLModel, table=False):
    """Update Document Request model."""

    name: str | None = Field(
        default=Undefined,
        min_length=1,
        max_length=100,
        description=DOC_NAME,
    )

    @field_validator("name")
    def validate_name(cls, v: str | None) -> str | None:
        """Validate the name field if provided (i.e. it's not None).

        The name field, if provided, and when stripped, must not be empty.

        Args:
            v (str): Name value.

        Raises:
            ValueError: If the name is invalid.

        Returns:
            str | None: Name value.
        """
        if v is not None and not v.strip():
            raise ValueError(NAME_NOT_EMP)

        return v


class AgentQueryRequest(SQLModel, table=False):
    """Agent query request model."""

    text: str = Field(min_length=1, max_length=1000, description=QUERY_TEXT)

    @field_validator("text")
    def validate_text(cls, v: str) -> str:
        """Validate the text field.

        The text field, when stripped, must not be empty.

        Args:
            v (str): Text value.

        Raises:
            ValueError: If the text is invalid.

        Returns:
            str: Text value.
        """
        if not v.strip():
            raise ValueError("Text must not be empty.")

        return v
