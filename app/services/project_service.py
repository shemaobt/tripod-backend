from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.project import (
    OrganizationMember,
    Project,
    ProjectOrganizationAccess,
    ProjectUserAccess,
)
from app.services.organization_service import is_member


async def get_project_by_id(db: AsyncSession, project_id: str) -> Project | None:
    stmt: Select[tuple[Project]] = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


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


async def grant_user_access(
    db: AsyncSession,
    project_id: str,
    user_id: str,
) -> ProjectUserAccess:
    existing: Select[tuple[ProjectUserAccess]] = select(ProjectUserAccess).where(
        ProjectUserAccess.project_id == project_id,
        ProjectUserAccess.user_id == user_id,
    )
    result = await db.execute(existing)
    existing_access = result.scalar_one_or_none()
    if existing_access:
        return existing_access
    access = ProjectUserAccess(project_id=project_id, user_id=user_id)
    db.add(access)
    await db.commit()
    await db.refresh(access)
    return access


async def grant_organization_access(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
) -> ProjectOrganizationAccess:
    existing: Select[tuple[ProjectOrganizationAccess]] = select(ProjectOrganizationAccess).where(
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


async def get_project_or_404(db: AsyncSession, project_id: str) -> Project:
    project = await get_project_by_id(db, project_id)
    if not project:
        raise NotFoundError("Project not found")
    return project


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
