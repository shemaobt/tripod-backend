from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.project import Organization, OrganizationMember


async def get_organization_by_id(db: AsyncSession, organization_id: str) -> Organization | None:
    stmt: Select[tuple[Organization]] = select(Organization).where(
        Organization.id == organization_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_organization_by_slug(db: AsyncSession, slug: str) -> Organization | None:
    stmt: Select[tuple[Organization]] = select(Organization).where(
        Organization.slug == slug.lower()
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_organization(db: AsyncSession, name: str, slug: str) -> Organization:
    existing = await get_organization_by_slug(db, slug)
    if existing:
        raise ConflictError("Organization slug already exists")
    org = Organization(name=name, slug=slug.lower())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


async def add_member(
    db: AsyncSession,
    organization_id: str,
    user_id: str,
    role: str = "member",
) -> OrganizationMember:
    stmt: Select[tuple[OrganizationMember]] = select(OrganizationMember).where(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == user_id,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ConflictError("User is already a member")
    member = OrganizationMember(
        organization_id=organization_id,
        user_id=user_id,
        role=role,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def get_organization_or_404(db: AsyncSession, organization_id: str) -> Organization:
    org = await get_organization_by_id(db, organization_id)
    if not org:
        raise NotFoundError("Organization not found")
    return org


async def is_member(db: AsyncSession, user_id: str, organization_id: str) -> bool:
    stmt: Select[tuple[OrganizationMember]] = select(OrganizationMember).where(
        OrganizationMember.user_id == user_id,
        OrganizationMember.organization_id == organization_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
