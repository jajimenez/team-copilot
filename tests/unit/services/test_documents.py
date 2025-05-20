"""Team Copilot Tests - Unit Tests - Services - Documents."""

from os.path import join
from unittest.mock import patch, call, MagicMock

import pytest

from team_copilot.core.config import settings
from team_copilot.models.data import Document, DocumentStatus

from team_copilot.services.documents import (
    get_all_documents,
    get_document,
    get_document_file_path,
    save_document,
    process_document,
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

        # Check function calls
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

        # Check function calls
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

        # Check function calls
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

        # Call the function being tested
        save_document(doc)

        # Check function calls
        mock_open_session.assert_called_once()
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

        # Check function calls
        mock_open_session.assert_called_once()
        mock_session.add.assert_called_once_with(doc)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(doc)


class TestProcessDocument:
    """Tests for the `team_copilot.services.documents.process_document` function."""

    
    @patch("team_copilot.services.documents.remove")
    @patch("team_copilot.services.documents.get_embedding")
    @patch("team_copilot.services.documents.get_text")
    @patch("team_copilot.services.documents.open_session")
    @patch("team_copilot.services.documents.get_document_file_path")
    def test_process_document(
        self,
        mock_get_document_file_path: MagicMock,
        mock_open_session: MagicMock,
        mock_get_text: MagicMock,
        mock_get_embedding: MagicMock,
        mock_remove: MagicMock,
        test_documents: list[Document],
    ):
        """Test processing a document.

        Args:
            mock_get_document_file_path (MagicMock): Mock object for the
                "get_document_file_path" function.
            mock_open_session (MagicMock): Mock object for the "open_session" function.
            mock_get_text (MagicMock): Mock object for the "get_text" function.
            mock_get_embedding (MagicMock): Mock object for the "get_embedding"
                function.
            mock_remove (MagicMock): Mock object for the "remove" function.
            test_documents (list[Document]): Test documents.
        """
        # Get a test document
        doc = test_documents[0]

        # Test values
        file_path = "/tmp/document.pdf"
        chunks = ["Chunk 1", "Chunk 2"]
        embedding = [0.1, 0.2, 0.3]

        # Simulate the returned value of the "get_document_file_path" function
        mock_get_document_file_path.return_value = file_path

        # Simulate the returned value of the "get_text" function
        mock_get_text.return_value = chunks

        # Simulate the returned value of the "get_embedding" function
        mock_get_embedding.return_value = embedding

        # Create mock session and configure it to return the test document
        mock_session = MagicMock()
        mock_session.get.return_value = doc

        # Simulate the returned value of the "open_session" function
        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested
        process_document(doc.id)

        # Check function calls
        mock_get_document_file_path.assert_called_once_with(doc.id)
        mock_open_session.assert_called_once()
        mock_session.get.assert_called_once_with(Document, doc.id)
        assert mock_session.add.call_count == 3
        assert mock_session.commit.call_count == 3
        mock_get_text.assert_called_once_with(file_path)
        assert mock_session.delete.call_count == 2
        assert mock_get_embedding.call_count == 2
        mock_remove.assert_called_once_with(file_path)

        # Check that the document status has been updated to Completed
        assert doc.status == DocumentStatus.COMPLETED

    @patch("team_copilot.services.documents.remove")
    @patch("team_copilot.services.documents.exists", return_value=True)
    @patch("team_copilot.services.documents.get_text")
    @patch("team_copilot.services.documents.open_session")
    @patch("team_copilot.services.documents.get_document_file_path")
    def test_get_text_exception(
        self,
        mock_get_document_file_path: MagicMock,
        mock_open_session: MagicMock,
        mock_get_text: MagicMock,
        mock_exists: MagicMock,
        mock_remove: MagicMock,
        test_documents: list[Document],
    ):
        """Test processing a document when an exception occurs in the "get_text"
        function.

        Args:
            mock_get_document_file_path (MagicMock): Mock object for the
                "get_document_file_path" function.
            mock_open_session (MagicMock): Mock object for the "open_session" function.
            mock_get_text (MagicMock): Mock object for the "get_text" function.
            mock_exists (MagicMock): Mock object for the "exists" function.
            mock_remove (MagicMock): Mock object for the "remove" function.
            test_documents (list[Document]): Test documents.
        """
        # Get a test document
        doc = test_documents[0]

        # Test values
        file_path = "/tmp/document.pdf"

        # Simulate the returned value of the "get_document_file_path" function
        mock_get_document_file_path.return_value = file_path

        # Create mock session and configure it to return the test document
        mock_session = MagicMock()
        mock_session.get.return_value = doc

        # Simulate the returned value of the "open_session" function
        mock_open_session.return_value.__enter__.return_value = mock_session

        # Simulate the exception in the "get_text" function
        error = "Error getting text from document."
        mock_get_text.side_effect = Exception(error)

        # Call the function being tested and check that an exception is raised
        with pytest.raises(Exception, match=error):
            process_document(doc.id)

        # Check that the document status has been updated to Failed
        assert doc.status == DocumentStatus.FAILED

        # Check function calls
        mock_get_document_file_path.assert_called_once_with(doc.id)
        mock_open_session.assert_called_once()
        mock_session.get.assert_called_once_with(Document, doc.id)
        mock_session.add.assert_called_once_with(doc)
        mock_session.commit.call_count == 2
        mock_get_text.assert_called_once_with(file_path)
        mock_exists.assert_called_once_with(file_path)
        mock_remove.assert_called_once_with(file_path)
