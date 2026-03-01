from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.db.models.phase import PhaseDependency
from app.services.phase.get_phase_or_404 import get_phase_or_404


async def add_dependency(
    db: AsyncSession,
    phase_id: str,
    depends_on_id: str,
) -> PhaseDependency:
    await get_phase_or_404(db, phase_id)
    await get_phase_or_404(db, depends_on_id)
    if phase_id == depends_on_id:
        raise ConflictError("Phase cannot depend on itself")
    existing: Select[tuple[PhaseDependency]] = select(PhaseDependency).where(
        PhaseDependency.phase_id == phase_id,
        PhaseDependency.depends_on_id == depends_on_id,
    )
    result = await db.execute(existing)
    if result.scalar_one_or_none():
        raise ConflictError("Dependency already exists")
    dep = PhaseDependency(phase_id=phase_id, depends_on_id=depends_on_id)
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    return dep
