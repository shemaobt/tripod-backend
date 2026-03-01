from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.org import OrganizationMember


async def is_member(db: AsyncSession, user_id: str, organization_id: str) -> bool:
    stmt: Select[tuple[OrganizationMember]] = select(OrganizationMember).where(
        OrganizationMember.user_id == user_id,
        OrganizationMember.organization_id == organization_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
