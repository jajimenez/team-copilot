"""Team Copilot - Database - Setup."""

from sqlmodel import create_engine, SQLModel
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Import all data models to ensure that they are registered with SQLModel. Otherwise,
# the "SQLModel.metadata.create_all" function wouldn't create the tables in the
# database.
from team_copilot.models.data import *

from team_copilot.core.config import settings
from team_copilot.core.auth import get_user, create_user


def setup(db_url: str):
    """Setup the database.

    The following steps are performed:

      1. Create the UUID and vector extensions.
      2. Create the tables.
      3. Create the vector column ("embedding") index for similarity search.
      4. Create an administrator user if the "TEAM_COPILOT_APP_ADMIN_USER" and
         "TEAM_COPILOT_APP_ADMIN_PASSWORD" environment variables are set.

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

    # Create an administrator user if the "TEAM_COPILOT_APP_ADMIN_USER" and
    # "TEAM_COPILOT_APP_ADMIN_PASSWORD" environment variables are set and the user does
    # not already exist.
    if settings.app_admin_user is not None and settings.app_admin_password is not None:
        if not get_user(settings.app_admin_user):
            create_user(
                settings.app_admin_user,
                settings.app_admin_password,
                name="Administrator",
                staff=True,
                admin=True,
                enabled=True,
            )
