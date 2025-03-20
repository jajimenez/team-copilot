"""Team Copilot - Core - Models."""

from sqlalchemy import (
    Column,
    UUID,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    text,
    func,
)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from team_copilot.core.types import VectorType


Base = declarative_base()


class Document(Base):
    """Document model."""

    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )

    name = Column(String, nullable=False)
    path = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all",
    )


class DocumentChunk(Base):
    """Document chunk model."""

    __tablename__ = "document_chunks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="cascade"),
        nullable=False,
    )

    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(VectorType, nullable=False)

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="unique_document_chunk",
        ),
    )
