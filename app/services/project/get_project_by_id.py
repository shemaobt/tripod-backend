from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project


async def get_project_by_id(db: AsyncSession, project_id: str) -> Project | None:
    stmt: Select[tuple[Project]] = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
