"""Team Copilot - Database - Setup."""

from sqlmodel import create_engine, SQLModel
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Import all models to ensure that they are registered with SQLModel. Otherwise, the
# "SQLModel.metadata.create_all" function wouldn't create the tables in the database.
from team_copilot.models.models import *


def setup(db_url: str):
    """Setup the database.

    The following steps are performed:

      1. Create the UUID and vector extensions.
      2. Create the tables.
      3. Create the vector column ("embedding") index for similarity search.

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
    SQLModel.metadata.create_all(engine)

    # Create the vector column ("embedding") index for similarity search
    with engine.begin() as con:
        con.execute(
            text(
                "CREATE INDEX IF NOT EXISTS document_chunks_embedding_index "
                "ON document_chunks "
                "USING hnsw(embedding vector_cosine_ops);"
            )
        )
