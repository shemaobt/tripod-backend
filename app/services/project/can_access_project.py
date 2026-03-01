from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import ProjectOrganizationAccess, ProjectUserAccess
from app.services.org.is_member import is_member


async def can_access_project(
    db: AsyncSession,
    user_id: str,
    project_id: str,
) -> bool:
    user_access: Select[tuple[ProjectUserAccess]] = select(ProjectUserAccess).where(
        ProjectUserAccess.project_id == project_id,
        ProjectUserAccess.user_id == user_id,
    )
    result = await db.execute(user_access)
    if result.scalar_one_or_none():
        return True
    org_access = select(ProjectOrganizationAccess.organization_id).where(
        ProjectOrganizationAccess.project_id == project_id
    )
    orgs_with_access = (await db.execute(org_access)).scalars().all()
    for org_id in orgs_with_access:
        if await is_member(db, user_id, org_id):
            return True
    return False
