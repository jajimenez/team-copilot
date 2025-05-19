"""Team Copilot Tests - Unit Tests - Services - Search."""

import pytest
from unittest.mock import patch, MagicMock

from team_copilot.services.search import (
    get_most_similar_chunks,
    NO_EMB,
    ERROR_GET_CHUNKS,
)

from team_copilot.models.data import DocumentChunk


class TestGetMostSimilarChunks:
    """Tests for the `team_copilot.services.search.get_most_similar_chunks` function."""

    @patch("team_copilot.services.search.get_embedding")
    @patch("team_copilot.services.search.open_session")
    def test_get_most_similar_chunks(
        self,
        mock_open_session: MagicMock,
        mock_get_embedding: MagicMock,
    ):
        """Test getting the most similar chunks.
        
        Args:
            mock_open_session (MagicMock): Mock "mock_open_session" function.
            mock_get_embedding (MagicMock): Mock "get_embedding" function.
        """
        # Mock embedding function returned value
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock session object. The first call to "exec" returns document chunk IDs. The
        # second call, followed by a call to "all", returns DocumentChunk objects.
        mock_ids = [(1,), (2,), (3,)]
        mock_doc_chunks = MagicMock()

        mock_doc_chunks.all.return_value = [
            DocumentChunk(id=1, chunk_text="Chunk 1", embedding=[0.1, 0.2, 0.3]),
            DocumentChunk(id=2, chunk_text="Chunk 2", embedding=[0.2, 0.3, 0.4]),
            DocumentChunk(id=3, chunk_text="Chunk 3", embedding=[0.3, 0.4, 0.5]),
        ]

        mock_session = MagicMock()
        mock_session.exec.side_effect = [mock_ids, mock_doc_chunks]

        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested
        query = "Test query."
        result = get_most_similar_chunks(query, limit=3)

        # Check result
        assert len(result) == 3

        for i in range(3):
            chunk_id = i + 1
            assert result[i].id == chunk_id
            assert result[i].chunk_text == f"Chunk {chunk_id}"

        # Check function calls
        mock_get_embedding.assert_called_once_with(query, "query")
        assert mock_session.exec.call_count == 2

    @patch("team_copilot.services.search.get_embedding")
    @patch("team_copilot.services.search.open_session")
    def test_no_chunks_found(
        self,
        mock_open_session: MagicMock,
        mock_get_embedding: MagicMock,
    ):
        """Test with no similar chunks found.

        Args:
            mock_open_session (MagicMock): Mock "mock_open_session" function.
            mock_get_embedding (MagicMock): Mock "get_embedding" function.
        """
        # Mock embedding function returned value
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock session object. The first call to "exec" returns document chunk IDs. The
        # second call, followed by a call to "all", returns DocumentChunk objects.
        mock_ids = []

        mock_doc_chunks = MagicMock()
        mock_doc_chunks.all.return_value = []

        mock_session = MagicMock()
        mock_session.exec.side_effect = [mock_ids, mock_doc_chunks]

        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested
        query = "Test query."
        result = get_most_similar_chunks(query)

        # Check result
        assert result == []

        # Check function calls
        mock_get_embedding.assert_called_once_with(query, "query")
        mock_session.exec.assert_called_once()

    @patch("team_copilot.services.search.get_embedding")
    def test_no_embedding_found(self, mock_get_embedding: MagicMock):
        """Test when no embedding is found for the query.

        Args:
            mock_get_embedding (MagicMock): Mock "get_embedding" function.
        """
        # Mock embedding function returned value
        mock_get_embedding.return_value = None

        # Call the function being tested and check that a ValueError exception is raised
        query = "Test query."

        with pytest.raises(ValueError) as exc:
            get_most_similar_chunks(query)

        # Check the error message
        e = NO_EMB.format(query)
        assert e in str(exc.value)

        # Check function calls
        mock_get_embedding.assert_called_once_with(query, "query")

    @patch("team_copilot.services.search.get_embedding")
    @patch("team_copilot.services.search.open_session")
    def test_db_error(
        self,
        mock_open_session: MagicMock,
        mock_get_embedding: MagicMock,
    ):
        """Test when there is a database error.

        Args:
            mock_open_session (MagicMock): Mock "mock_open_session" function.
            mock_get_embedding (MagicMock): Mock "get_embedding" function.
        """
        # Mock embedding function returned value
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock session object. A call to "exec" raises an exception.
        mock_session = MagicMock()
        mock_session.exec.side_effect = Exception("Database connection error")

        mock_open_session.return_value.__enter__.return_value = mock_session

        # Call the function being tested and check that an exception is raised
        query = "Test query."

        with pytest.raises(Exception) as exc:
            get_most_similar_chunks(query)

        # Check the error message
        e = ERROR_GET_CHUNKS.format(query, "Database connection error")
        assert e in str(exc.value)

        # Check function calls
        mock_get_embedding.assert_called_once_with(query, "query")
