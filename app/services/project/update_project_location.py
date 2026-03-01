from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project
from app.services.project.get_project_or_404 import get_project_or_404


async def update_project_location(
    db: AsyncSession,
    project_id: str,
    *,
    latitude: float | None = None,
    longitude: float | None = None,
    location_display_name: str | None = None,
) -> Project:
    project = await get_project_or_404(db, project_id)
    if latitude is not None:
        project.latitude = latitude
    if longitude is not None:
        project.longitude = longitude
    if location_display_name is not None:
        project.location_display_name = location_display_name
    await db.commit()
    await db.refresh(project)
    return project
