"""Team Copilot Tests - Unit Tests - Services - Extraction."""

from unittest.mock import patch, MagicMock

from team_copilot.services.extraction import get_text

from tests.unit.conftest import (
    DOC_1_PAG_1_TXT,
    DOC_1_PAG_2_IMG_TXT,
    DOC_3_PAG_1_TXT,
    DOC_4_PAG_1_TXT,
)


class TestGetEmbedding:
    """Tests for the `team_copilot.services.extraction.get_text` function."""

    def test_get_text(self, test_pdf_doc_path: str, mock_pdf_doc_1: MagicMock):
        """Test getting the text from a PDF with a text page and an image page.

        Args:
            test_pdf_doc_path (str): Test PDF document path.
            mock_pdf_doc_1 (MagicMock): Mock PDF document.
        """
        with (
            patch("fitz.open", return_value=mock_pdf_doc_1),
            patch("team_copilot.services.extraction.Image.frombytes"),
            patch("pytesseract.image_to_string", return_value=DOC_1_PAG_2_IMG_TXT)
        ):
            # Call the function being tested
            chunks = get_text(test_pdf_doc_path)

        # Check result
        assert len(chunks) == 2

        assert DOC_1_PAG_1_TXT in chunks[0]
        assert DOC_1_PAG_2_IMG_TXT in chunks[1]

    def test_chunks(self, test_pdf_doc_path: str, mock_pdf_doc_2: MagicMock):
        """Test the chunks when getting the text from a PDF with one page where the text
        is larger than the chunk size.

        Args:
            test_pdf_doc_path (str): Test PDF document path.
            mock_pdf_doc_2 (MagicMock): Mock PDF document.
        """
        # With a chunk size of 800 and an overlap of 200, a document page with a
        # 2000-character text like "DOC_2_PAG_1_TXT" would be split into 3 chunks:
        #   - Chunk 1: Characters 0-799.
        #   - Chunk 2: Characters 599-1399.
        #   - Chunk 3: Characters 1199-1999.
        chunk_size = 800
        overlap = 200

        with patch("fitz.open", return_value=mock_pdf_doc_2):
            # Call the function being tested
            chunks = get_text(test_pdf_doc_path, chunk_size, overlap)

            # Check result

            # Check the number of chunks
            assert len(chunks) == 3

            # Check the size of each chunk
            for i in range(3):
                assert len(chunks[i]) == chunk_size

    def test_no_chunking(self, test_pdf_doc_path: str, mock_pdf_doc_3: MagicMock):
        """Test that there is no chunking (i.e. there is only one chunk) when getting
        the text from a PDF with one page where the text is shorter than the chunk size.

        Args:
            test_pdf_doc_path (str): Test PDF document path.
            mock_pdf_doc_3 (MagicMock): Mock PDF document.
        """    
        with patch("fitz.open", return_value=mock_pdf_doc_3):
            # Call the function being tested
            chunks = get_text(test_pdf_doc_path, chunk_size=1000)

        # Check result
        assert len(chunks) == 1
        assert chunks[0] == DOC_3_PAG_1_TXT

    def test_min_viable_chunk_size(
        self,
        test_pdf_doc_path: str,
        mock_pdf_doc_4: MagicMock,
    ):
        """Test that chunks smaller than the minimum viable chunk size are discarded.

        Args:
            test_pdf_doc_path (str): Test PDF document path.
            mock_pdf_doc_4 (MagicMock): Mock PDF document.
        """
        chunk_size = 1000
        overlap = 5

        with patch("fitz.open", return_value=mock_pdf_doc_4):
            # Call the function being tested
            chunks = get_text(test_pdf_doc_path, chunk_size=chunk_size, overlap=overlap)

        # Check result
        assert len(chunks) == 1
        assert chunks[0] == DOC_4_PAG_1_TXT[:chunk_size]
