from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.project import ProjectOrganizationAccess


async def revoke_organization_access(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
) -> None:
    stmt: Select[tuple[ProjectOrganizationAccess]] = select(ProjectOrganizationAccess).where(
        ProjectOrganizationAccess.project_id == project_id,
        ProjectOrganizationAccess.organization_id == organization_id,
    )
    result = await db.execute(stmt)
    access = result.scalar_one_or_none()
    if not access:
        raise NotFoundError("Organization access not found for this project")
    await db.delete(access)
    await db.commit()
