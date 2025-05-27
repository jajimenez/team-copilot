"""Team Copilot - Services - Users."""

from datetime import datetime, timezone
from uuid import UUID
import logging

from sqlmodel import select, or_

from team_copilot.db.session import open_session
from team_copilot.models.data import User
from team_copilot.core.config import settings


# Messages
ERROR_DEL_USER = "Error deleting user {} ({}): {}."
GET_USER_ARG = "At least, the ID or the username must be provided."
USER_CRE = "User {} ({}) created."
USER_DEL = "User {} ({}) deleted."
USER_NF = "User {} not found."
USER_UPD = "User {} ({}) updated."

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_users() -> list[User]:
    """Get all users.

    Returns:
        list[User]: Users.
    """
    with open_session(settings.db_url) as session:
        # Create statement
        s = select(User)

        # Execute the statement and return all elements
        return session.exec(s).all()


def get_user(
    id: UUID | None = None,
    username: str | None = None,
    email: str | None = None,
) -> User | None:
    """Get a user by its ID, username or e-mail address.

    Args:
        id (UUID | None): User ID.
        username (str | None): Username.
        email (str | None): E-mail address.

    Returns:
        User | None: User if found, None otherwise.
    """
    if id is None and username is None and email is None:
        raise ValueError(GET_USER_ARG)

    with open_session(settings.db_url) as session:
        conditions = []

        if id is not None:
            conditions.append(User.id == id)

        if username is not None:
            conditions.append(User.username == username)

        if email is not None:
            conditions.append(User.email == email)

        # Create the statement
        s = select(User).where(or_(*conditions))

        # Execute the statement and return the first element
        return session.exec(s).first()


def save_user(user: User):
    """Save a user to the database.

    If the user is new, the ID in the `User` object is set to the ID generated
    automatically by the database server. If the user already exists, its "updated_at"
    field is updated to the current time.

    Args:
        user (User): User to save.
    """
    with open_session(settings.db_url) as session:
        # Add user to the session
        session.add(user)

        # Check if the user already exists (it exists if the ID in the User object is
        # set). If it exists, update the "updated_at" field.
        if user.id:
            update = True
            user.updated_at = datetime.now(timezone.utc)
        else:
            update = False

        # Commit the changes to the database
        session.commit()

        if update:
            logger.info(USER_UPD.format(user.id, user.username))
        else:
            logger.info(USER_CRE.format(user.id, user.username))

        # Refresh the user to get the ID
        session.refresh(user)


def delete_user(id: UUID):
    """Delete a user from the database.

    Args:
        id (UUID): User ID.

    Raises:
        ValueError: If the user is not found.
    """
    with open_session(settings.db_url) as session:
        # Check if the user exists
        user = session.get(User, id)

        if not user:
            m = USER_NF.format(id)
            logger.error(m)

            raise ValueError(m)

        try:
            # Delete the document from the database
            session.delete(user)

            # Commit the changes to the database
            session.commit()
            logger.info(USER_DEL.format(user.id, user.username))
        except Exception as e:
            logger.error(ERROR_DEL_USER.format(user.id, user.username, e))

            # Re-raise the exception
            raise
