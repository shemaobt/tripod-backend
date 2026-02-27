from datetime import UTC, datetime

from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RoleError
from app.db.models.auth import App, Role, User, UserAppRole


async def get_app_by_key(db: AsyncSession, app_key: str) -> App | None:
    """Fetch app by key."""
    stmt: Select[tuple[App]] = select(App).where(App.app_key == app_key)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_role(db: AsyncSession, app_id: str, role_key: str) -> Role | None:
    """Fetch role by app and role key."""
    stmt: Select[tuple[Role]] = select(Role).where(Role.app_id == app_id, Role.role_key == role_key)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def has_role(db: AsyncSession, user_id: str, app_key: str, role_key: str) -> bool:
    """Return whether user has an active role for app."""
    app = await get_app_by_key(db, app_key)
    if not app:
        return False

    role = await get_role(db, app.id, role_key)
    if not role:
        return False

    stmt: Select[tuple[UserAppRole]] = select(UserAppRole).where(
        UserAppRole.user_id == user_id,
        UserAppRole.app_id == app.id,
        UserAppRole.role_id == role.id,
        UserAppRole.revoked_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def assert_can_manage_roles(db: AsyncSession, actor_user: User, app_key: str) -> None:
    """Assert actor can assign and revoke roles for an app."""
    if actor_user.is_platform_admin:
        return
    if await has_role(db, actor_user.id, app_key, "admin"):
        return
    raise RoleError("Actor cannot manage roles for this app")


async def assign_role(
    db: AsyncSession,
    actor_user: User,
    target_user_id: str,
    app_key: str,
    role_key: str,
) -> UserAppRole:
    """Assign role to a target user in app context."""
    await assert_can_manage_roles(db, actor_user, app_key)

    app = await get_app_by_key(db, app_key)
    if not app:
        raise RoleError("App not found")

    role = await get_role(db, app.id, role_key)
    if not role:
        raise RoleError("Role not found")

    stmt: Select[tuple[UserAppRole]] = select(UserAppRole).where(
        UserAppRole.user_id == target_user_id,
        UserAppRole.app_id == app.id,
        UserAppRole.role_id == role.id,
        UserAppRole.revoked_at.is_(None),
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()
    if assignment:
        return assignment

    assignment = UserAppRole(
        user_id=target_user_id,
        app_id=app.id,
        role_id=role.id,
        granted_by=actor_user.id,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def revoke_role(
    db: AsyncSession,
    actor_user: User,
    target_user_id: str,
    app_key: str,
    role_key: str,
) -> UserAppRole:
    """Revoke an active role assignment."""
    await assert_can_manage_roles(db, actor_user, app_key)

    app = await get_app_by_key(db, app_key)
    if not app:
        raise RoleError("App not found")

    role = await get_role(db, app.id, role_key)
    if not role:
        raise RoleError("Role not found")

    stmt: Select[tuple[UserAppRole]] = select(UserAppRole).where(
        UserAppRole.user_id == target_user_id,
        UserAppRole.app_id == app.id,
        UserAppRole.role_id == role.id,
        UserAppRole.revoked_at.is_(None),
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise RoleError("Active assignment not found")

    assignment.revoked_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def list_roles(db: AsyncSession, user_id: str, app_key: str | None = None) -> list[tuple[str, str]]:
    """List active role keys for user, optionally filtered by app."""
    stmt = (
        select(App.app_key, Role.role_key)
        .join(Role, Role.app_id == App.id)
        .join(
            UserAppRole,
            and_(UserAppRole.role_id == Role.id, UserAppRole.app_id == App.id),
        )
        .where(UserAppRole.user_id == user_id, UserAppRole.revoked_at.is_(None))
    )
    if app_key:
        stmt = stmt.where(App.app_key == app_key)
    result = await db.execute(stmt)
    return [(row[0], row[1]) for row in result.all()]
