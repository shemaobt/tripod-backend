from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.project import Project
from app.services.project.get_project_by_id import get_project_by_id


async def get_project_or_404(db: AsyncSession, project_id: str) -> Project:
    project = await get_project_by_id(db, project_id)
    if not project:
        raise NotFoundError("Project not found")
    return project
