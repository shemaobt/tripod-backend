from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.phase import PhaseDependency
from app.services.phase.get_phase_or_404 import get_phase_or_404


async def list_dependencies(db: AsyncSession, phase_id: str) -> list[PhaseDependency]:
    await get_phase_or_404(db, phase_id)
    stmt = (
        select(PhaseDependency)
        .where(PhaseDependency.phase_id == phase_id)
        .order_by(PhaseDependency.depends_on_id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
