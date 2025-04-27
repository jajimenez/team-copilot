"""Team Copilot - Services - Documents."""

from voyageai import Client

from team_copilot.core.config import settings


# Messages
NO_EMB_FOUND = "No embedding found in the API response."


def get_embedding(text: str, input_type: str) -> list[float]:
    """Get the embedding for a given text.

    This function uses the Voyage AI API to get the embedding.

    Args:
        text (str): Text.
        input_type (str): Input type ("document" or "query").

    Raises:
        ValueError: If the input type is invalid or if no embedding is found in the API
            response.

    Returns:
        list[float]: Text embedding (vector).
    """
    # Check the input type
    if input_type not in ["document", "query"]:
        raise ValueError(f'Invalid input type: "{input_type}".')

    # Voyage AI API client
    client = Client(
        api_key=settings.emb_api_key,
        max_retries=settings.emb_max_retries,
        timeout=settings.emb_timeout_sec,
    )

    # Make the request to the Voyage AI API
    res = client.embed(
        model=settings.emb_model,
        input_type=input_type,
        texts=[text],
    )

    # Get the embedding from the API response
    emb = res.embeddings[0]

    if not emb:
        raise ValueError(NO_EMB_FOUND)

    return emb
