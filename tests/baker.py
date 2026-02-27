from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.auth import App, RefreshToken, Role, User, UserAppRole
from app.db.models.project import (
    Language,
    Organization,
    OrganizationMember,
    Project,
    ProjectOrganizationAccess,
    ProjectUserAccess,
)
from app.services.auth_service import hash_password


async def make_user(
    db: AsyncSession,
    *,
    email: str = "user@example.com",
    password: str = "password123",
    display_name: str | None = "Test User",
    is_active: bool = True,
    is_platform_admin: bool = False,
) -> User:
    user = User(
        email=email.lower(),
        password_hash=hash_password(password),
        display_name=display_name,
        is_active=is_active,
        is_platform_admin=is_platform_admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def make_app(
    db: AsyncSession,
    *,
    app_key: str = "test-app",
    name: str = "Test App",
    is_active: bool = True,
) -> App:
    app = App(app_key=app_key, name=name, is_active=is_active)
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


async def make_role(
    db: AsyncSession,
    app_id: str,
    *,
    role_key: str = "member",
    label: str = "Member",
    description: str | None = None,
    is_system: bool = False,
) -> Role:
    role = Role(
        app_id=app_id,
        role_key=role_key,
        label=label,
        description=description,
        is_system=is_system,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def make_user_app_role(
    db: AsyncSession,
    user_id: str,
    app_id: str,
    role_id: str,
    *,
    granted_by: str | None = None,
    revoked_at: datetime | None = None,
) -> UserAppRole:
    assignment = UserAppRole(
        user_id=user_id,
        app_id=app_id,
        role_id=role_id,
        granted_by=granted_by,
        revoked_at=revoked_at,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def make_language(
    db: AsyncSession,
    *,
    name: str = "Test Language",
    code: str = "tst",
) -> Language:
    lang = Language(name=name, code=code.lower())
    db.add(lang)
    await db.commit()
    await db.refresh(lang)
    return lang


async def make_organization(
    db: AsyncSession,
    *,
    name: str = "Test Org",
    slug: str = "test-org",
) -> Organization:
    org = Organization(name=name, slug=slug.lower())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


async def make_organization_member(
    db: AsyncSession,
    user_id: str,
    organization_id: str,
    *,
    role: str = "member",
) -> OrganizationMember:
    member = OrganizationMember(
        user_id=user_id,
        organization_id=organization_id,
        role=role,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def make_project(
    db: AsyncSession,
    language_id: str,
    *,
    name: str = "Test Project",
    description: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    location_display_name: str | None = None,
) -> Project:
    project = Project(
        name=name,
        language_id=language_id,
        description=description,
        latitude=latitude,
        longitude=longitude,
        location_display_name=location_display_name,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def make_project_user_access(
    db: AsyncSession,
    project_id: str,
    user_id: str,
) -> ProjectUserAccess:
    access = ProjectUserAccess(project_id=project_id, user_id=user_id)
    db.add(access)
    await db.commit()
    await db.refresh(access)
    return access


async def make_project_organization_access(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
) -> ProjectOrganizationAccess:
    access = ProjectOrganizationAccess(
        project_id=project_id,
        organization_id=organization_id,
    )
    db.add(access)
    await db.commit()
    await db.refresh(access)
    return access


async def make_refresh_token(
    db: AsyncSession,
    user_id: str,
    *,
    token_hash: str = "a" * 64,
    expires_at: datetime | None = None,
    revoked_at: datetime | None = None,
) -> RefreshToken:
    if expires_at is None:
        expires_at = datetime.now(UTC) + timedelta(days=7)
    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked_at=revoked_at,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
