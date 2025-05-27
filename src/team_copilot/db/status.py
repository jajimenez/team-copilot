"""Team Copilot - Database - Status."""

from sqlmodel import create_engine
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.base import Connection


def _check_vector_ext(con: Connection) -> bool:
    """Check the Pgvector extension.

    Args:
        con (Connection): Database connection.

    Returns:
        bool: Whether the extension is installed.
    """
    res = con.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
    )

    return bool(res.scalar())


def _check_vector_ops(con: Connection) -> bool:
    """Check the vector operations.

    Args:
        con (Connection): Database connection.

    Returns:
        bool: Whether the vector operations work.
    """
    res = con.execute(
        text("SELECT '[1, 2, 3]'::vector + '[4, 5, 6]'::vector AS distance;")
    )

    return res.scalar() is not None


def _check_tables(con: Connection) -> bool:
    """Check the tables.

    Args:
        con (Connection): Database connection.

    Returns:
        bool: Whether the tables exist.
    """
    res = con.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name IN ('documents', 'document_chunks');"
        )
    )

    tables = [r[0] for r in res]
    return "documents" in tables and "document_chunks" in tables


def check_status(db_url: str) -> bool:
    """Check the status of the database.

    Args:
        db_url (str): Database URL ("postgresql://user:password@localhost/db").

    Returns:
        bool: Whether the database is available.
    """
    try:
        eng: Engine = create_engine(db_url)

        with eng.connect() as con:
            # Check the extension, vector operations and tables
            return (
                _check_vector_ext(con) and _check_vector_ops(con) and _check_tables(con)
            )
    except Exception:
        return False
