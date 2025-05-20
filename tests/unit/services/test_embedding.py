"""Team Copilot Tests - Unit Tests - Services - Embedding."""

from unittest.mock import patch, MagicMock

import pytest

from team_copilot.services.embedding import get_embedding, NO_EMB


class TestGetEmbedding:
    """Tests for the `team_copilot.services.embedding.get_embedding` function."""

    @patch("team_copilot.services.embedding.Client")
    def test_get_document_emb(self, mock_client: MagicMock):
        """Test gettting a document embedding.

        Args:
            mock_client (Mock): Mock object for the
                "team_copilot.services.embedding.Client" class.
        """
        # Test embedding
        emb = [0.1, 0.2, 0.3]

        # Mock the value returned by the "Client.embed" method
        mock_result = MagicMock()
        mock_result.embeddings = [emb]

        mock_instance = MagicMock()
        mock_instance.embed.return_value = mock_result

        # Mock instances of the mock "Client" class
        mock_client.return_value = mock_instance

        # Call the function being tested
        embedding = get_embedding("Test document.", "document")

        # Check result
        assert embedding == emb

        # Check function calls
        mock_instance.embed.assert_called_once()

    @patch("team_copilot.services.embedding.Client")
    def test_get_query_emb(self, mock_client: MagicMock):
        """Test gettting a query embedding.

        Args:
            mock_client (Mock): Mock object for the
                "team_copilot.services.embedding.Client" class.
        """
        # Test embedding
        emb = [0.1, 0.2, 0.3]

        # Mock the value returned by the "Client.embed" method
        mock_result = MagicMock()
        mock_result.embeddings = [emb]

        mock_instance = MagicMock()
        mock_instance.embed.return_value = mock_result

        # Mock instances of the mock "Client" class
        mock_client.return_value = mock_instance

        # Call the function being tested
        embedding = get_embedding("Test query.", "query")

        # Check result
        assert embedding == emb

        # Check function calls
        mock_instance.embed.assert_called_once()

    def test_invalid_input_type(self):
        """Test getting an embedding with an invalid input type."""
        input_type = "invalid"

        with pytest.raises(ValueError, match=f"Invalid input type: {input_type}"):
            get_embedding("Test text.", input_type)

    @patch("team_copilot.services.embedding.Client")
    def test_no_embedding(self, mock_client: MagicMock):
        """Test getting an embedding when no embedding is returned.

        Args:
            mock_client (Mock): Mock object for the
                "team_copilot.services.embedding.Client" class.
        """
        # Mock the value returned by the "Client.embed" method
        mock_result = MagicMock()
        mock_result.embeddings = [[]]  # Empty embedding

        mock_instance = MagicMock()
        mock_instance.embed.return_value = mock_result

        # Mock instances of the mock "Client" class
        mock_client.return_value = mock_instance

        # Call the function being tested (for both document and query input types )and
        # check that a ValueError exception is raised.
        for i in ["document", "query"]:
            with pytest.raises(ValueError, match=NO_EMB):
                get_embedding("Test text", i)
