from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.phase import Phase


async def get_phase_by_id(db: AsyncSession, phase_id: str) -> Phase | None:
    stmt: Select[tuple[Phase]] = select(Phase).where(Phase.id == phase_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
