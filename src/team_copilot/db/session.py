"""Team Copilot - Database - Session."""

from typing import Generator

from sqlmodel import create_engine, Session
from sqlalchemy.engine import Engine


# Engine cache to avoid creating multiple engines for the same database URL
_engines: dict[str, Engine] = {}


def _get_engine(db_url: str) -> Engine:
    """Get or create a database engine.

    Args:
        db_url (str): Database URL ("postgresql://user:password@localhost/db").

    Returns:
        Engine: SQLAlchemy engine.
    """
    if db_url not in _engines:
        _engines[db_url] = create_engine(db_url)

    return _engines[db_url]


def get_session(db_url: str) -> Generator[Session, None, None]:
    """Get a database session for dependency injection.

    Args:
        db_url (str): Database URL ("postgresql://user:password@localhost/db").

    Returns:
        Generator[Session, None, None]: Generator that yields a database session.
    """
    engine = _get_engine(db_url)

    with Session(engine) as session:
        yield session


def open_session(db_url: str) -> Session:
    """Open a database session.

    Args:
        db_url (str): Database URL ("postgresql://user:password@localhost/db").

    Returns:
        Session: SQLAlchemy session.
    """
    engine = _get_engine(db_url)
    return Session(engine)
