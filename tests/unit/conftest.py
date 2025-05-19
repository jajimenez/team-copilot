"""Team Copilot Tests - Unit Tests - Configuration."""

from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from team_copilot.models.data import User


DOC_1_PAG_1_TXT = "a" * 500
DOC_1_PAG_2_TXT = "b"
DOC_1_PAG_2_IMG_TXT = "c" * 500

DOC_2_PAG_1_TXT = "d" * 2000
DOC_3_PAG_1_TXT = "e" * 500
DOC_4_PAG_1_TXT = "f" * 1150


@pytest.fixture
def test_users() -> list[User]:
    """Get test users.

    Returns:
        list[User]: Test users.
    """
    now = datetime.now(timezone.utc)

    return [
        User(
            id=uuid4(),
            username="user1",
            password="user1user1",
            name="User 1",
            email="user1@example.com",
            staff=False,
            admin=False,
            enabled=True,
            created_at=now,
            updated_at=now,
        ),
        User(
            id=uuid4(),
            username="user2",
            password="user2user2",
            name="User 2",
            email="user2@example.com",
            staff=False,
            admin=False,
            enabled=True,
            created_at=now,
            updated_at=now,
        ),
    ]


@pytest.fixture
def test_pdf_doc_path() -> str:
    """Get a test PDF document path.

    Returns:
        str: Test PDF document path.
    """
    return "/tmp/mock_document.pdf"


@pytest.fixture
def mock_pdf_doc_1() -> MagicMock:
    """Get a mock PDF document with a text page and an image page where the text of each
    page is shorter than the chunk size (1000 characters by default).

    Returns:
        MagicMock: Mock PDF document.
    """
    mock_doc = MagicMock()

    # Create a mock text-based page, with a text long enough to be extracted directly
    # (100 characters or more).
    mock_txt_pag = MagicMock()
    mock_txt_pag.get_text.return_value = DOC_1_PAG_1_TXT

    # Create a mock image-based page, with a text short enough to trigger OCR (less than
    # 100 characters).
    mock_img_pag = MagicMock()
    mock_img_pag.get_text.return_value = DOC_1_PAG_2_TXT

    test_pixmap = MagicMock()
    test_pixmap.width = 100
    test_pixmap.height = 100
    test_pixmap.samples = b"Test image data"

    mock_img_pag.get_pixmap.return_value = test_pixmap

    mock_doc.__iter__.return_value = [mock_txt_pag, mock_img_pag]
    return mock_doc


@pytest.fixture
def mock_pdf_doc_2() -> MagicMock:
    """Get a mock PDF document with a text page where the text is larger than the chunk
    size (1000 characters by default).

    Returns:
        MagicMock: Mock PDF document.
    """
    mock_doc = MagicMock()

    # Create a mock text-based page, with a text long enough to be extracted directly
    # (100 characters or more).
    mock_txt_pag = MagicMock()
    mock_txt_pag.get_text.return_value = DOC_2_PAG_1_TXT

    mock_doc.__iter__.return_value = [mock_txt_pag]
    return mock_doc


@pytest.fixture
def mock_pdf_doc_3() -> MagicMock:
    """Get a mock PDF document with a text page where the text is shorter than the chunk
    size (1000 characters by default).

    Returns:
        MagicMock: Mock PDF document.
    """
    mock_doc = MagicMock()

    # Create a mock text-based page, with a text long enough to be extracted directly
    # (100 characters or more).
    mock_txt_pag = MagicMock()
    mock_txt_pag.get_text.return_value = DOC_3_PAG_1_TXT

    mock_doc.__iter__.return_value = [mock_txt_pag]
    return mock_doc


@pytest.fixture
def mock_pdf_doc_4() -> MagicMock:
    """Get a mock PDF document with a text page where the text is slightly larger than
    the chunk size (1000 characters by default), so that only one chunk should be
    extracted and the raminder should be discarded as it has less than the minimum
    viable chunk size (200 characters).

    Returns:
        MagicMock: Mock PDF document.
    """
    mock_doc = MagicMock()

    # Create a mock text-based page, with a text long enough to be extracted directly
    # (100 characters or more).
    mock_txt_pag = MagicMock()
    mock_txt_pag.get_text.return_value = DOC_4_PAG_1_TXT

    mock_doc.__iter__.return_value = [mock_txt_pag]
    return mock_doc
