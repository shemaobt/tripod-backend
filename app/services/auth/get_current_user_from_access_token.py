from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.db.models.auth import User
from app.services.auth.get_user_by_id import get_user_by_id
from app.utils.jwt import decode_token


async def get_current_user_from_access_token(db: AsyncSession, token: str) -> User:
    """Resolve current user from access token."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    user = await get_user_by_id(db, payload["sub"])
    if not user:
        raise AuthenticationError("User not found")
    if not user.is_active:
        raise AuthorizationError("Inactive user")
    return user
