from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.phase import Phase
from app.models.phase import PhaseCreate


async def create_phase(db: AsyncSession, payload: PhaseCreate) -> Phase:
    phase = Phase(name=payload.name, description=payload.description)
    db.add(phase)
    await db.commit()
    await db.refresh(phase)
    return phase
