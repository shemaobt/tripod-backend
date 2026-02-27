from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.project import Language


async def get_language_by_id(db: AsyncSession, language_id: str) -> Language | None:
    stmt: Select[tuple[Language]] = select(Language).where(Language.id == language_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_language_by_code(db: AsyncSession, code: str) -> Language | None:
    stmt: Select[tuple[Language]] = select(Language).where(Language.code == code.lower())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_languages(db: AsyncSession) -> list[Language]:
    stmt: Select[tuple[Language]] = select(Language).order_by(Language.code)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_language(db: AsyncSession, name: str, code: str) -> Language:
    existing = await get_language_by_code(db, code)
    if existing:
        raise ConflictError("Language code already exists")
    language = Language(name=name, code=code.lower())
    db.add(language)
    await db.commit()
    await db.refresh(language)
    return language


async def get_language_or_404(db: AsyncSession, language_id: str) -> Language:
    language = await get_language_by_id(db, language_id)
    if not language:
        raise NotFoundError("Language not found")
    return language
