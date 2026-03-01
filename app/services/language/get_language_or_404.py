from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.language import Language
from app.services.language.get_language_by_id import get_language_by_id


async def get_language_or_404(db: AsyncSession, language_id: str) -> Language:
    language = await get_language_by_id(db, language_id)
    if not language:
        raise NotFoundError("Language not found")
    return language
