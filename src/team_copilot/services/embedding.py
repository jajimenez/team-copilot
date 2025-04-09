"""Team Copilot - Services - Documents."""

import time
import logging

import requests
from requests import RequestException

from team_copilot.core.config import settings


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Messages
ERROR_GET_EMB = 'Error getting the embedding (attempt {}): "{}".'
NO_EMB_FOUND = "No embedding found."


def get_embedding(text: str, max_attempts: int = 3) -> list[float]:
    """Get the embedding for a given text.

    Args:
        text (str): Text.
        max_attempts (int): Maximum number of attempts to get the embedding
            (default: 3).

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
