"""Team Copilot - Services - Extraction."""

import fitz
from PIL import Image
import pytesseract


def get_text(file_path: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """Extract text from a PDF file.

    Args:
        file_path (str): PDF file path.
        chunk_size (int): Target size of each text chunk.
        overlap (int): Overlap size between consecutive chunks in characters
            (default: 100).

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
