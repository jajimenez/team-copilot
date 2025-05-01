"""Team Copilot - Models - Request Models."""

from pydantic import field_validator
from sqlmodel import SQLModel, Field

from team_copilot.models.data import User


USERNAME = "Username"
PASSWORD = "Password"
DOC_NAME = "Document name"
QUERY_TEXT = "Query text"


class UpdateUserRequest(SQLModel, table=False):
    """Update User request model."""

    username: str = Field(min_length=3, max_length=100)
    name: str | None = Field(min_length=1, max_length=100)
    email: str | None = Field(min_length=3, max_length=100)
    staff: bool | None = False
    admin: bool = False
    enabled: bool = False


class CreateUserRequest(UpdateUserRequest):
    """Create User request model."""

    password: str = Field(min_length=8, max_length=200)

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


class UpdateUserPasswordRequest(SQLModel, table=False):
    """Update User Password request model."""

    password: str = Field(min_length=8, max_length=200)


class DocumentRequest(SQLModel, table=False):
    """Document request model."""

    name: str = Field(min_length=1, max_length=100, description=DOC_NAME)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate the name field.

        The name field, when stripped, must not be empty.

        Args:
            v (str): Name value.

        Raises:
            ValueError: If the name is empty after stripping.

        Returns:
            str: Name value.
        """
        if not v.strip():
            raise ValueError("Name must not be empty.")

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
            ValueError: If the text is empty after stripping.

        Returns:
            str: Text value.
        """
        if not v.strip():
            raise ValueError("Text must not be empty.")

        return v
