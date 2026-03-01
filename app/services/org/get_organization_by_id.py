from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.org import Organization


async def get_organization_by_id(db: AsyncSession, organization_id: str) -> Organization | None:
    stmt: Select[tuple[Organization]] = select(Organization).where(
        Organization.id == organization_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
