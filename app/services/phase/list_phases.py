from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.phase import Phase, ProjectPhase


async def list_phases(
    db: AsyncSession,
    project_id: str | None = None,
) -> list[Phase]:
    if project_id is not None:
        stmt = (
            select(Phase)
            .join(ProjectPhase, ProjectPhase.phase_id == Phase.id)
            .where(ProjectPhase.project_id == project_id)
            .order_by(Phase.name)
        )
    else:
        stmt = select(Phase).order_by(Phase.name)
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())
