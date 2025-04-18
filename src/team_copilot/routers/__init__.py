"""Team Copilot - Routers."""

# Messages
INVALID_CREDENTIALS = "Invalid credentials"
UNAUTHORIZED = "Unauthorized"


def get_value_error_str(e: ValueError) -> str:
    """Get a formatted string from a ValueError exception.

    Args:
        e (ValueError): ValueError exception.

    Returns:
        str: Formatted string.
    """
    errors = [i["msg"] for i in e.errors()]
    return ". ".join(errors)
