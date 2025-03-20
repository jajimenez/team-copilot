"""Team Copilot - Core - Database."""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.base import Connection

from team_copilot.core.models import Base


def setup_db(db_url: str):
    """Setup the database.

    Args:
        db_url (str): Database URL ("postgresql://user:password@localhost/db").
    """
    # Create engine
    engine: Engine = create_engine(db_url)

    # Create the UUID and vector extensions
    with engine.begin() as con:
        con.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        con.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

    # Create the tables
    Base.metadata.create_all(engine)

    # Create the vector column ("embedding") index for similarity search
    with engine.begin() as con:
        con.execute(
            text(
                "CREATE INDEX IF NOT EXISTS document_chunks_embedding_index "
                "ON document_chunks "
                "USING hnsw(embedding vector_cosine_ops);"
            )
        )


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


def check_db_status(con_str: str) -> bool:
    """Check the status of the database.

    Args:
        con_str (str): Database connection string.

    Returns:
        bool: Whether the database is available.
    """
    try:
        # Connect to the database
        eng: Engine = create_engine(con_str)

        with eng.connect() as con:
            # Check the extension, vector operations and tables
            return (
                _check_vector_ext(con) and _check_vector_ops(con) and _check_tables(con)
            )
    except Exception:
        return False
