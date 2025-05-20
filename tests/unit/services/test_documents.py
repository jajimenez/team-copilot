"""Team Copilot Tests - Unit Tests - Services - Documents."""

from os.path import join
from unittest.mock import patch, MagicMock

import pytest

from team_copilot.core.config import settings
from team_copilot.models.data import Document

from team_copilot.services.documents import (
    get_all_documents,
    get_document,
    get_document_file_path,
    save_document,
)


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
            mock_open_session (MagicMock): Mock object for the "open_session" function.
            test_documents (list[Document]): Test documents.
        """
        # Create mock session and configure it to return the test documents
        mock_session = MagicMock()
        mock_session.exec.return_value.all.return_value = test_documents

        # Simulate the returned value of the "open_session" function
        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested
        result = get_all_documents()

        # Check result
        assert result == test_documents

        # Check that the session was used correctly
        mock_open_session.assert_called_once()
        mock_session.exec.assert_called_once()
        mock_session.exec.return_value.all.assert_called_once()


class TestGetDocument:
    """Tests for the `team_copilot.services.documents.get_document` function."""

    @patch("team_copilot.services.documents.open_session")
    def test_get_document_by_id(
        self,
        mock_open_session: MagicMock,
        test_documents: list[Document],
    ):
        """Test getting a document by ID.

        Args:
            mock_open_session (MagicMock): Mock object for the "open_session" function.
            test_documents (list[Document]): Test documents.
        """
        # Get a test document
        doc = test_documents[0]

        # Create mock session and configure it to return the test document
        mock_session = MagicMock()
        mock_session.exec.return_value.first.return_value = doc

        # Simulate the returned value of the "open_session" function
        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested
        result = get_document(id=doc.id)

        # Check result
        assert result == doc

        # Check that the session was used correctly
        mock_open_session.assert_called_once()
        mock_session.exec.assert_called_once()
        mock_session.exec.return_value.first.assert_called_once()

    @patch("team_copilot.services.documents.open_session")
    def test_get_document_by_name(
        self,
        mock_open_session: MagicMock,
        test_documents: list[Document],
    ):
        """Test getting a document by name.

        Args:
            mock_open_session (MagicMock): Mock object for the "open_session" function.
            test_documents (list[Document]): Test documents.
        """
        # Get a test document
        doc = test_documents[0]

        # Create mock session and configure it to return the test document
        mock_session = MagicMock()
        mock_session.exec.return_value.first.return_value = doc

        # Simulate the returned value of the "open_session" function
        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested
        result = get_document(name=doc.name)

        # Check result
        assert result == doc

        # Check that the session was used correctly
        mock_open_session.assert_called_once()
        mock_session.exec.assert_called_once()
        mock_session.exec.return_value.first.assert_called_once()

    def no_args(self):
        """Test getting a document with no arguments."""
        # Call the function and check that a ValueError exception is raised
        with pytest.raises(
            ValueError,
            match="At least, the ID or the name must be provided.",
        ):
            get_document()


class TestGetDocumentFilePath:
    """Tests for the `team_copilot.services.documents.get_document_file_path` function.
    """

    def test_get_document_file_path(self, test_documents: list[Document]):
        """Test getting the document file path.

        Args:
            test_documents (list[Document]): Test documents.
        """
        # Get a test document
        doc = test_documents[0]

        # Call the function being tested
        result = get_document_file_path(doc_id=doc.id)

        # Check result
        assert result == join(settings.app_temp_dir, f"{doc.id}.pdf")


class TestSaveDocument:
    """Tests for the `team_copilot.services.documents.save_document` function."""

    @patch("team_copilot.services.documents.open_session")
    def test_save_new_document(
        self,
        mock_open_session: MagicMock,
        test_documents: list[Document],
    ):
        """Test saving a new document to the database.

        Args:
            mock_open_session (MagicMock): Mock object for the "open_session" function.
            test_documents (list[Document]): Test documents.
        """
        # Get a test document and remove its ID
        doc = test_documents[0]
        doc.id = None

        # Create mock session
        mock_session = MagicMock()

        # Simulate the returned value of the "open_session" function
        mock_open_session.return_value.__enter__.return_value = mock_session
        
        # Call the function
        save_document(doc)
        
        # Assertions
        mock_session.add.assert_called_once_with(doc)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(doc)

    @patch("team_copilot.services.documents.open_session")
    def test_save_existing_document(
        self,
        mock_open_session: MagicMock,
        test_documents: list[Document],
    ):
        """Test saving an existing document to the database.

        Args:
            mock_open_session (MagicMock): Mock object for the "open_session" function.
            test_documents (list[Document]): Test documents.
        """
        # Get a test document (with an ID)
        doc = test_documents[0]

        # Create mock session
        mock_session = MagicMock()

        # Simulate the returned value of the "open_session" function
        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested
        save_document(doc)

        # Check that the session was used correctly
        mock_session.add.assert_called_once_with(doc)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(doc)
