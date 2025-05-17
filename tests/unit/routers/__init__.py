"""Team Copilot Tests - Unit Tests - Routers."""

from fastapi import status, HTTPException


def raise_not_authorized_exc():
    """Raise an HTTPException with a 403 status code and a "Not authorized" message.
    
    Raises:
        HTTPException: HTTPException exception with a 403 status code and
            a "Not authorized" message.
    """
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
