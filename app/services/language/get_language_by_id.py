from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.language import Language


async def get_language_by_id(db: AsyncSession, language_id: str) -> Language | None:
    stmt: Select[tuple[Language]] = select(Language).where(Language.id == language_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
