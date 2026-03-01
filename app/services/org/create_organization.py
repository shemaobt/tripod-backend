from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.db.models.org import Organization
from app.services.org.get_organization_by_slug import get_organization_by_slug


async def create_organization(db: AsyncSession, name: str, slug: str) -> Organization:
    existing = await get_organization_by_slug(db, slug)
    if existing:
        raise ConflictError("Organization slug already exists")
    org = Organization(name=name, slug=slug.lower())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org
