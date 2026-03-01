from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.phase import ProjectPhase
from app.services.phase.get_phase_or_404 import get_phase_or_404


async def list_projects_for_phase(db: AsyncSession, phase_id: str) -> list[str]:
    await get_phase_or_404(db, phase_id)
    stmt = select(ProjectPhase.project_id).where(ProjectPhase.phase_id == phase_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
