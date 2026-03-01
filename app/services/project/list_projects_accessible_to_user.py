from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.org import OrganizationMember
from app.db.models.project import (
    Project,
    ProjectOrganizationAccess,
    ProjectUserAccess,
)


async def list_projects_accessible_to_user(
    db: AsyncSession,
    user_id: str,
) -> list[Project]:
    direct_project_ids = select(ProjectUserAccess.project_id).where(
        ProjectUserAccess.user_id == user_id
    )
    user_org_ids = select(OrganizationMember.organization_id).where(
        OrganizationMember.user_id == user_id
    )
    via_org_project_ids = select(ProjectOrganizationAccess.project_id).where(
        ProjectOrganizationAccess.organization_id.in_(user_org_ids)
    )
    stmt = (
        select(Project)
        .where(
            or_(
                Project.id.in_(direct_project_ids),
                Project.id.in_(via_org_project_ids),
            )
        )
        .order_by(Project.name)
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())
