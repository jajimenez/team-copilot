"""Team Copilot Tests - Unit Tests - Services - Documents."""

from unittest.mock import patch, MagicMock

from team_copilot.models.data import Document
from team_copilot.services.documents import get_all_documents


class TestGetAllDocuments:
    """Tests for the `team_copilot.services.documents.get_all_documents` function."""

    def test_get_all_documents(self, test_documents: list[Document]):
        """Test getting all the documents.

        Args:
            test_documents (list[Document]): Test documents.
        """
        # Create mock session
        mock_session = MagicMock()
        mock_session.exec.return_value.all.return_value = test_documents

        # Mock the "open_session" function
        with patch("team_copilot.services.documents.open_session") as mock_os:
            mock_os.return_value.__enter__.return_value = mock_session

            # Call the function being tested
            result = get_all_documents()

            # Check result
            assert result == test_documents

            # Check that the session was used correctly
            mock_os.assert_called_once()
            mock_session.exec.assert_called_once()
