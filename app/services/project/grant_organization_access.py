from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import ProjectOrganizationAccess


async def grant_organization_access(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
) -> ProjectOrganizationAccess:
    existing: Select[tuple[ProjectOrganizationAccess]] = select(
        ProjectOrganizationAccess
    ).where(
        ProjectOrganizationAccess.project_id == project_id,
        ProjectOrganizationAccess.organization_id == organization_id,
    )
    result = await db.execute(existing)
    existing_access = result.scalar_one_or_none()
    if existing_access:
        return existing_access
    access = ProjectOrganizationAccess(
        project_id=project_id,
        organization_id=organization_id,
    )
    db.add(access)
    await db.commit()
    await db.refresh(access)
    return access
