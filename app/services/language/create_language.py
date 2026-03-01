from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.db.models.language import Language
from app.services.language.get_language_by_code import get_language_by_code


async def create_language(db: AsyncSession, name: str, code: str) -> Language:
    existing = await get_language_by_code(db, code)
    if existing:
        raise ConflictError("Language code already exists")
    language = Language(name=name, code=code.lower())
    db.add(language)
    await db.commit()
    await db.refresh(language)
    return language
