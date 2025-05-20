"""Team Copilot Tests - Unit Tests - Services - Documents."""

from unittest.mock import patch, MagicMock

from team_copilot.models.data import Document
from team_copilot.services.documents import get_all_documents


class TestGetAllDocuments:
    """Tests for the `team_copilot.services.documents.get_all_documents` function."""

    @patch("team_copilot.services.documents.open_session")
    def test_get_all_documents(
        self,
        mock_open_session: MagicMock,
        test_documents: list[Document],
    ):
        """Test getting all the documents.

        Args:
            mock_open_session (MagicMock): Mock object for the object for the
                "open_session" function.
            test_documents (list[Document]): Test documents.
        """
        # Create mock session
        mock_session = MagicMock()
        mock_session.exec.return_value.all.return_value = test_documents

        # Mock the returned value of the "open_session" function
        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested
        result = get_all_documents()

        # Check result
        assert result == test_documents

        # Check that the session was used correctly
        mock_open_session.assert_called_once()
        mock_session.exec.assert_called_once()
        mock_session.exec.return_value.all.assert_called_once()
