from collections.abc import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthorizationError
from app.db.models.auth import User
from app.services import auth_service, authorization_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    return await auth_service.get_current_user_from_access_token(db, token)


def require_role(app_key: str, role_key: str) -> Callable:
    async def _check_role(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        allowed = await authorization_service.has_role(db, user.id, app_key, role_key)
        if not allowed and not user.is_platform_admin:
            raise AuthorizationError("Forbidden")
        return user

    return _check_role
