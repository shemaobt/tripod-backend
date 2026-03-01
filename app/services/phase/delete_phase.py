from sqlalchemy.ext.asyncio import AsyncSession

from app.services.phase.get_phase_or_404 import get_phase_or_404


async def delete_phase(db: AsyncSession, phase_id: str) -> None:
    phase = await get_phase_or_404(db, phase_id)
    await db.delete(phase)
    await db.commit()
