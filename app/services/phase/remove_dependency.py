from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.phase import PhaseDependency
from app.services.phase.get_phase_or_404 import get_phase_or_404


async def remove_dependency(
    db: AsyncSession,
    phase_id: str,
    depends_on_id: str,
) -> None:
    await get_phase_or_404(db, phase_id)
    await get_phase_or_404(db, depends_on_id)
    stmt = select(PhaseDependency).where(
        PhaseDependency.phase_id == phase_id,
        PhaseDependency.depends_on_id == depends_on_id,
    )
    result = await db.execute(stmt)
    dep = result.scalar_one_or_none()
    if dep:
        await db.delete(dep)
        await db.commit()
