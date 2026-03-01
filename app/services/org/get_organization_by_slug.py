from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.org import Organization


async def get_organization_by_slug(db: AsyncSession, slug: str) -> Organization | None:
    stmt: Select[tuple[Organization]] = select(Organization).where(
        Organization.slug == slug.lower()
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
