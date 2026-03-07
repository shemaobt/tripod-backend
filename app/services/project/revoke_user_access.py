from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.project import ProjectUserAccess


async def revoke_user_access(
    db: AsyncSession,
    project_id: str,
    user_id: str,
) -> None:
    stmt: Select[tuple[ProjectUserAccess]] = select(ProjectUserAccess).where(
        ProjectUserAccess.project_id == project_id,
        ProjectUserAccess.user_id == user_id,
    )
    result = await db.execute(stmt)
    access = result.scalar_one_or_none()
    if not access:
        raise NotFoundError("User access not found for this project")
    await db.delete(access)
    await db.commit()
