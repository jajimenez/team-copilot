"""Team Copilot - Database."""

from os import getenv

from sqlalchemy import create_engine, text, Engine
from sqlalchemy.engine.base import Connection


def _check_extension(con: Connection) -> bool:
    """Check the Pgvector extension.

    Args:
        con (Connection): Database connection.

    Returns:
        bool: Whether the extension is installed.
    """
    res = con.execute(text(
        "SELECT extname FROM pg_extension WHERE extname = 'vector';"
    ))

    return bool(res.scalar())


def _check_vector_operations(con: Connection) -> bool:
    """Check the vector operations.
    
    Args:
        con (Connection): Database connection.
    
    Returns:
        bool: Whether the vector operations work.
    """
    res = con.execute(text(
        "SELECT '[1, 2, 3]'::vector + '[4, 5, 6]'::vector AS distance;"
    ))

    return res.scalar() is not None


def _check_tables(con: Connection) -> bool:
    """Check the tables.

    Args:
        con (Connection): Database connection.

    Returns:
        bool: Whether the tables exist.
    """
    res = con.execute(text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_name IN ('documents', 'document_chunks');"
    ))

    tables = [r[0] for r in res]
    return  "documents" in tables and "document_chunks" in tables


def check_status() -> bool:
    """Check the status of the database.
    
    Returns:
        bool: Whether the database is available.
    """
    # Check the connection string environment variable
    con_str = getenv("TEAM_COPILOT_DB_CONNECTION")

    if not con_str:
        return False

    try:
        # Connect to the database
        eng: Engine = create_engine(con_str)

        with eng.connect() as con:
            # Check the extension, vector operations and tables
            return (
                _check_extension(con) and
                _check_vector_operations(con) and
                _check_tables(con)
            )
    except Exception:
        return False
