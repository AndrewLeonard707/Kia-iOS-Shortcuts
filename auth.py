"""Authentication dependency for FastAPI endpoints."""

import os
import logging

from fastapi import Header, HTTPException

logger = logging.getLogger(__name__)

SECRET_KEY: str = os.environ.get("SECRET_KEY", "")


def verify_auth(authorization: str = Header(...)) -> str:
    """Validate the Authorization header against SECRET_KEY.

    Raises 403 if the key is missing or does not match.
    Returns the validated key on success.
    """
    if not SECRET_KEY:
        logger.error("SECRET_KEY env var is not set -- all requests will be rejected")
        raise HTTPException(status_code=403, detail="Server misconfigured: no secret key")

    if authorization != SECRET_KEY:
        logger.warning("Unauthorized request: incorrect Authorization header")
        raise HTTPException(status_code=403, detail="Unauthorized")

    return authorization
