"""Team Copilot - Database - Session."""

from typing import Generator

from sqlmodel import create_engine, Session
from sqlalchemy.engine import Engine


def get_session(db_url: str) -> Generator[Session, None, None]:
    """Get a database session.

    Args:
        db_url (str): Database URL ("postgresql://user:password@localhost/db").

    Returns:
        Generator[Session, None, None]: Generator that yields a database session.
    """
    engine: Engine = create_engine(db_url)

    with Session(engine) as session:
        yield session
