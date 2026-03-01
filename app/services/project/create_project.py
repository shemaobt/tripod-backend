from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project


async def create_project(
    db: AsyncSession,
    name: str,
    language_id: str,
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
