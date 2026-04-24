import copy
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.db.models.book_context import BCDStatus, BookContextDocument
from app.services.book_context.get_bcd import get_bcd_or_404
from app.services.i18n.back_translate_content import back_translate_content

EDITABLE_SECTIONS = frozenset(
    {
        "structural_outline",
        "participant_register",
        "discourse_threads",
        "theological_spine",
        "places",
        "objects",
        "institutions",
        "genre_context",
        "maintenance_notes",
    }
)


async def update_section(
    db: AsyncSession,
    bcd_id: str,
    section_key: str,
    data: Any,
    user_id: str,
    locale: str = "en",
) -> BookContextDocument:
    """Update a BCD section, keeping the per-locale translation cache coherent.

    English remains the canonical source. On any save, the English field is
    overwritten. The translation cache is then reconciled so that:

    - If ``locale == "en"``: the edited ``section_key`` is dropped from every
      cached non-English locale (they are now stale). Other sections' caches
      are preserved.
    - If ``locale != "en"``: the user's original (non-English) payload is
      back-translated to English and stored at the top level, and the raw
      payload is preserved verbatim under ``translations[locale][section_key]``.
      The same ``section_key`` is dropped from every other cached locale.
    """
    bcd = await get_bcd_or_404(db, bcd_id)

    if bcd.status == BCDStatus.APPROVED:
        raise ConflictError(
            "Cannot edit an approved Book Context Document. Create a new version instead."
        )

    if bcd.status == BCDStatus.GENERATING:
        raise ConflictError("Cannot edit a document that is currently being generated.")

    if section_key not in EDITABLE_SECTIONS:
        raise NotFoundError(f"Unknown section: {section_key}")

    if not bcd.locked_by:
        raise ConflictError("You must lock the document before editing.")

    if bcd.locked_by != user_id:
        raise AuthorizationError("This document is locked by another user.")

    original_payload = data
    if locale and locale != "en" and isinstance(data, dict):
        english_data = await back_translate_content(data, locale)
    else:
        english_data = data

    setattr(bcd, section_key, english_data)

    translations = copy.deepcopy(bcd.translations) if bcd.translations else {}

    if locale and locale != "en":
        locale_cache = translations.get(locale)
        if not isinstance(locale_cache, dict):
            locale_cache = {}
            translations[locale] = locale_cache
        locale_cache[section_key] = original_payload

    for cached_locale in list(translations.keys()):
        if cached_locale == locale:
            continue
        sections = translations[cached_locale]
        if isinstance(sections, dict):
            sections.pop(section_key, None)
            if not sections:
                del translations[cached_locale]
        else:
            del translations[cached_locale]

    bcd.translations = translations if translations else None
    flag_modified(bcd, "translations")

    await db.commit()
    await db.refresh(bcd)
    return bcd
