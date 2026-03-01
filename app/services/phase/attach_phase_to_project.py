from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.db.models.phase import ProjectPhase
from app.services.phase.get_phase_or_404 import get_phase_or_404


async def attach_phase_to_project(
    db: AsyncSession,
    project_id: str,
    phase_id: str,
) -> ProjectPhase:
    from app.services.project.get_project_or_404 import get_project_or_404

    await get_project_or_404(db, project_id)
    await get_phase_or_404(db, phase_id)
    existing: Select[tuple[ProjectPhase]] = select(ProjectPhase).where(
        ProjectPhase.project_id == project_id,
        ProjectPhase.phase_id == phase_id,
    )
    result = await db.execute(existing)
    if result.scalar_one_or_none():
        raise ConflictError("Phase is already attached to this project")
    link = ProjectPhase(project_id=project_id, phase_id=phase_id)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link
