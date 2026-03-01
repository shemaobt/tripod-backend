from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.phase import ProjectPhase
from app.services.phase.get_phase_or_404 import get_phase_or_404


async def detach_phase_from_project(
    db: AsyncSession,
    project_id: str,
    phase_id: str,
) -> None:
    from app.services.project.get_project_or_404 import get_project_or_404

    await get_project_or_404(db, project_id)
    await get_phase_or_404(db, phase_id)
    stmt = select(ProjectPhase).where(
        ProjectPhase.project_id == project_id,
        ProjectPhase.phase_id == phase_id,
    )
    result = await db.execute(stmt)
    link = result.scalar_one_or_none()
    if link:
        await db.delete(link)
        await db.commit()
