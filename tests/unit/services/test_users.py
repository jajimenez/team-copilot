"""Team Copilot Tests - Unit Tests - Services - Users."""

from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest

from team_copilot.services.users import (
    get_all_users,
    get_user,
    save_user,
    delete_user,
    GET_USER_ARG,
    USER_NF,
)

from team_copilot.models.data import User


class TestGetAllUsers:
    """Tests for the `team_copilot.services.users.get_all_users` function."""

    def test_get_all_users(self, test_users: list[User]):
        """Test getting all the users.

        Args:
            test_users (list[User]): Test users.
        """
        # Create a mock database session and configure it to return our test users
        mock_session = MagicMock()
        mock_session.exec.return_value.all.return_value = test_users

        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session

            # Call the function being tested
            result = get_all_users()

            # Check result
            assert result == test_users

            # Check that the session was used correctly
            mock_os.assert_called_once()
            mock_session.exec.assert_called_once()


class TestGetUser:
    """Tests for the `team_copilot.services.users.get_user` function."""

    def test_get_by_id(self, test_users: list[User]):
        """Test getting a user by its ID.

        Args:
            test_users (list[User]): Test users.
        """
        # Test user
        user = test_users[0]

        # Create a mock session and configure it to return our test user
        mock_session = MagicMock()
        mock_session.exec.return_value.first.return_value = user

        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session

            # Call the function being tested
            result = get_user(id=user.id)

            # Check result
            assert result == user

    def test_get_by_username(self, test_users: list[User]):
        """Test getting a user by its username.

        Args:
            test_users (list[User]): Test users.
        """
        # Test user
        user = test_users[0]

        # Create a mock session and configure it to return our test user
        mock_session = MagicMock()
        mock_session.exec.return_value.first.return_value = user

        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session
  
            # Call the function being tested
            result = get_user(username=user.username)

            # Check result
            assert result == user

    def test_get_by_email(self, test_users: list[User]):
        """Test getting a user by its email address.

        Args:
            test_users (list[User]): Test users.
        """
        # Test user
        user = test_users[0]

        # Create a mock session and configure it to return our test user
        mock_session = MagicMock()
        mock_session.exec.return_value.first.return_value = user
        
        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session
            
            # Call the function being tested
            result = get_user(email=user.email)

            # Check result
            assert result == user

    def test_get_by_multiple_params(self, test_users: list[User]):
        """Test getting a user by multiple parameters.

        Args:
            test_users (list[User]): Test users.
        """
        # Test user
        user = test_users[0]

        # Create a mock session and configure it to return our test user
        mock_session = MagicMock()
        mock_session.exec.return_value.first.return_value = user
        
        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session
            
            # Call the function being tested
            result = get_user(id=user.id, username=user.username, email=user.email)

            # Check result
            assert result == user

    def test_no_parameters(self):
        """Test getting a user without any parameters."""
        # Call the function being tested and check that it raises a ValueError exception
        with pytest.raises(ValueError) as exc:
            get_user()

        # Check the error message
        assert str(exc.value) == GET_USER_ARG

    def test_non_existing_user(self):
        """Test getting a user that doesn't exist."""
        # Test user ID
        user_id = uuid4()

        # Create a mock session and configure it to return None (i.e. the user wasn't
        # found).
        mock_session = MagicMock()
        mock_session.exec.return_value.first.return_value = None

        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session

            # Call the function being tested
            result = get_user(id=user_id)

            # Check result
            assert result is None


class TestSaveUser:
    """Tests for the `team_copilot.services.users.save_user` function."""

    def test_save_new_user(self):
        """Test saving a new user to the database."""
        # Create a test new user (without ID)
        user = User(
            username="user",
            password="password",
            email="user@example.com",
            name="User",
        )

        # Create mock session
        mock_session = MagicMock()
        
        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session

            # Call the function being tested
            save_user(user)

            # Check that the session was used correctly
            mock_session.add.assert_called_once_with(user)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(user)

    def test_save_existing_user(self):
        """Test saving an existing user to the database."""
        user_id = uuid4()
        now = datetime.now(timezone.utc)

        # Create a test existing user (with ID)
        user = User(
            id=user_id,
            username="user",
            password="password",
            email="user@example.com",
            name="User",
            created_at=now,
            updated_at=now,
        )

        # Create mock session
        mock_session = MagicMock()

        # Mock the open_session function and datetime
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session
            
            # Call the function being tested
            save_user(user)
            
            # Check that the session was used correctly
            mock_session.add.assert_called_once_with(user)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(user)


class TestDeleteUser:
    """Tests for the `team_copilot.services.users.delete_user` function."""

    def test_delete_user(self, test_users: list[User]):
        """Test deleting a user.

        Args:
            test_users (list[User]): Test users.
        """
        # Test user
        user = test_users[0]

        # Create mock session and configure it to return our test user
        mock_session = MagicMock()
        mock_session.get.return_value = user

        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session

            # Call the function being tested
            delete_user(user.id)

            # Check that the session was used correctly
            mock_session.get.assert_called_once_with(User, user.id)
            mock_session.delete.assert_called_once_with(user)
            mock_session.commit.assert_called_once()
    
    def test_delete_non_existing_user(self):
        """Test deleting a user that doesn't exist."""
        # Test user ID
        user_id = uuid4()

        # Create mock session and configure it to return None (i.e. the user wasn't
        # found).
        mock_session = MagicMock()
        mock_session.get.return_value = None
        
        # Mock the open_session function
        with patch("team_copilot.services.users.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session

            # Call the function being tested and check that it raises a ValueError
            # exception.
            with pytest.raises(ValueError) as exc:
                delete_user(user_id)

            # Check the error message
            assert str(exc.value) == USER_NF.format(user_id)

            # Check that the session was used correctly
            mock_session.get.assert_called_once_with(User, user_id)
            mock_session.delete.assert_not_called()
            mock_session.commit.assert_not_called()
