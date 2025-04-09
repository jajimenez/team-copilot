"""Team Copilot - Services - Documents."""

import time
import logging

import fitz
from PIL import Image
import pytesseract

import requests
from requests import RequestException

from team_copilot.db.session import open_session
from team_copilot.models.models import Document, DocumentChunk, DocumentStatus
from team_copilot.core.config import settings


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Messages
ERROR_GET_EMB = 'Error getting the embedding (attempt {}): "{}".'
NO_EMB_FOUND = "No embedding found."
ERROR_PROC_DOC = 'Error processing document: "{}".'


def _save_doc(doc: Document):
    """Save a document to the database.

    Args:
        doc (Document): Document object.
    """
    with open_session(settings.app_db_url) as session:
        session.add(doc)
        session.commit()
        session.refresh(doc)


def _get_text(file_path: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """Extract text from a PDF file.

    Args:
        file_path (str): PDF file path.
        chunk_size (int): Target size of each text chunk.
        overlap (int): Overlap size between consecutive chunks in characters (default:
            100).

    Returns:
        list[str]: Extracted text chunks.
    """
    chunks = []

    # Open the PDF file
    doc = fitz.open(file_path)

    # Iterate through each page
    for page in doc:
        # Try to extract text directly
        text = page.get_text().strip()
        text_len = len(text)

        # If text is too short, the page might be an image
        if text_len < 100:
            # Get the page as an image
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Use OCR to extract text from the image
            ocr_text = pytesseract.image_to_string(img).strip()
            ocr_text_len = len(ocr_text)

            # If OCR text is found, use it instead. Otherwise, skip the page.
            if ocr_text_len > text_len:
                text = ocr_text
            else:
                continue

        # Split the text into smaller (overlapping) chunks if needed
        if text_len > chunk_size:
            for i in range(0, text_len, chunk_size - overlap):
                chunk = text[i : i + chunk_size]
            
                # Minimum viable chunk size
                if len(chunk) > 200:
                    chunks.append(chunk)
        else:
            chunks.append(text)

    return chunks


def _get_embedding(text: str, max_attempts: int = 3) -> list[float]:
    """Get the embedding for a given text.

    Args:
        text (str): Text.
        max_attempts (int): Maximum number of attempts to get the embedding (default: 3).

    Returns:
        list[float]: Text embedding (vector).
    """
    # Ollama embeddings endpoint
    url = f"{settings.ollama_url}/api/embeddings"

    # Request data
    data = {
        "model": settings.emb_model,
        "prompt": text,
    }

    attempt = 0

    while attempt < max_attempts:
        try:
            # Make the request
            res = requests.post(url, json=data)

            # Raise an exception if the request failed
            res.raise_for_status()

            # Get the embedding
            emb = res.json().get("embedding")

            if not emb:
                raise ValueError(NO_EMB_FOUND)

            return emb
        except (RequestException, ValueError) as e:
            logger.error(ERROR_GET_EMB.format(attempt + 1, e))
            attempt += 1

            # Re-raise the exception if the maximum number of attempts is reached
            if attempt >= max_attempts:
                raise

            # Wait for 1 second
            time.sleep(1)


def process_doc(doc: Document):
    """Process a document that has been uploaded.

    Args:
        doc (Document): Document object.
    """
    try:
        # Set the document status
        doc.status = DocumentStatus.PROCESSING

        # Save the document to the database
        _save_doc(doc)

        # Extract the text chunks from the document
        chunks: list[str] = _get_text(doc.path)

        # Get the embedding for each chunk and set the document chunks
        doc.chunks = [
            DocumentChunk(
                chunk_text=chunk,
                chunk_index=i,
                embedding=_get_embedding(chunk),
            )
            for i, chunk in enumerate(chunks)
        ]

        # Set the document status
        doc.status = DocumentStatus.COMPLETED

        # Save the document to the database
        _save_doc(doc)

    except Exception as e:
        logger.error(ERROR_PROC_DOC.format(e))

        # Update the document status to Failed
        doc.status = DocumentStatus.FAILED
        _save_doc(doc)

        # Re-raise the exception
        raise
