"""Team Copilot - Models - Request Models."""

from pydantic import field_validator
from sqlmodel import SQLModel, Field


DOC_TITLE = "Document title"


class DocumentRequest(SQLModel, table=False):
    """Document request model."""

    title: str = Field(min_length=1, max_length=100, description=DOC_TITLE)

    @field_validator("title")
    def validate_title(cls, v: str) -> str:
        """Validate the title field.

        The title field, when stripped, must not be empty.

        Args:
            v (str): Title value.

        Raises:
            ValueError: If the title is empty after stripping.

        Returns:
            str: Title value.
        """
        if not v.strip():
            raise ValueError("Title must not be empty.")

        return v
