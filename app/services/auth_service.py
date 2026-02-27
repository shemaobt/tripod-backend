import hashlib
from datetime import UTC, datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError, ConflictError
from app.db.models.auth import RefreshToken, User
from app.models.schemas import UserSignupRequest
from app.utils.jwt import create_token, decode_token

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_refresh_token(token: str) -> str:
    """Hash refresh token for database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email address."""
    stmt: Select[tuple[User]] = select(User).where(User.email == email.lower())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Get user by id."""
    stmt: Select[tuple[User]] = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def signup_user(db: AsyncSession, payload: UserSignupRequest) -> User:
    """Create a new local user."""
    existing_user = await get_user_by_email(db, payload.email)
    if existing_user:
        raise ConflictError("Email already exists")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """Authenticate user credentials and return user."""
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid credentials")
    if not user.is_active:
        raise AuthorizationError("Inactive user")
    return user


async def issue_tokens(db: AsyncSession, user: User) -> tuple[str, str]:
    """Issue access and refresh token pair and persist refresh token hash."""
    access_token = create_token(user.id, "access", settings.access_token_expire_minutes)
    refresh_token = create_token(user.id, "refresh", settings.refresh_token_expire_minutes)

    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    db.add(token_record)
    await db.commit()

    return access_token, refresh_token


async def revoke_refresh_token(db: AsyncSession, refresh_token: str) -> None:
    """Revoke an existing refresh token."""
    token_hash = hash_refresh_token(refresh_token)
    stmt: Select[tuple[RefreshToken]] = select(RefreshToken).where(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked_at.is_(None),
    )
    result = await db.execute(stmt)
    token_record = result.scalar_one_or_none()
    if token_record:
        token_record.revoked_at = datetime.now(UTC)
        await db.commit()


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
    """Validate refresh token and issue a new access token."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid token type")

    token_hash = hash_refresh_token(refresh_token)
    stmt: Select[tuple[RefreshToken]] = select(RefreshToken).where(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked_at.is_(None),
    )
    result = await db.execute(stmt)
    token_record = result.scalar_one_or_none()
    if not token_record:
        raise AuthenticationError("Refresh token revoked or missing")

    if token_record.expires_at < datetime.now(UTC):
        raise AuthenticationError("Refresh token expired")

    user = await get_user_by_id(db, payload["sub"])
    if not user or not user.is_active:
        raise AuthorizationError("Inactive or missing user")

    return create_token(user.id, "access", settings.access_token_expire_minutes)


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
