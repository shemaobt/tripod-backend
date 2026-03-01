import hashlib


def hash_refresh_token(token: str) -> str:
    """Hash refresh token for database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
