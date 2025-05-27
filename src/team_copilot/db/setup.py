"""Team Copilot - Database - Setup."""

import logging

from sqlmodel import create_engine, SQLModel
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Import all data models to ensure that they are registered with SQLModel. Otherwise,
# the "SQLModel.metadata.create_all" function wouldn't create the tables in the
# database.
from team_copilot.models.data import *

from team_copilot.models.data import User
from team_copilot.core.config import settings
from team_copilot.services.users import get_user, save_user


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        if not get_user(username=settings.app_admin_user):
            # Create the user object. The ID is set to None because it will be generated
            # automatically by the database server when the user is saved to the
            # database.
            user = User(
                username=settings.app_admin_user,
                password=settings.app_admin_password,
                name="Administrator",
                staff=True,
                admin=True,
                enabled=True,
            )

            # Save the user to the database. The password is hashed automatically and
            # the ID is set to the ID generated automatically by the database server.
            save_user(user)
