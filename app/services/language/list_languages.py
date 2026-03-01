from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.language import Language


async def list_languages(db: AsyncSession) -> list[Language]:
    stmt: Select[tuple[Language]] = select(Language).order_by(Language.code)
    result = await db.execute(stmt)
    return list(result.scalars().all())
