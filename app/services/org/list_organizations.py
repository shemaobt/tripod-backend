from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.org import Organization


async def list_organizations(db: AsyncSession) -> list[Organization]:
    stmt: Select[tuple[Organization]] = select(Organization).order_by(Organization.name)
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())
