from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.phase import Phase
from app.services.phase.get_phase_by_id import get_phase_by_id


async def get_phase_or_404(db: AsyncSession, phase_id: str) -> Phase:
    phase = await get_phase_by_id(db, phase_id)
    if not phase:
        raise NotFoundError("Phase not found")
    return phase
