from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.db.models.org import OrganizationMember


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
