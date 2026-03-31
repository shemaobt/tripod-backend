from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.db.models.book_context import BCDApproval, BCDStatus, BookContextDocument
from app.services.book_context.get_bcd import get_bcd_or_404


async def set_active_bcd(
    db: AsyncSession,
    bcd_id: str,
) -> BookContextDocument:

    bcd = await get_bcd_or_404(db, bcd_id)

    if bcd.status == BCDStatus.GENERATING:
        raise ConflictError("Cannot set a generating document as active.")

    await db.execute(
        update(BookContextDocument)
        .where(
            BookContextDocument.book_id == bcd.book_id,
            BookContextDocument.id != bcd_id,
            BookContextDocument.is_active,
        )
        .values(is_active=False)
    )

    await db.execute(delete(BCDApproval).where(BCDApproval.bcd_id == bcd_id))
    if bcd.status == BCDStatus.APPROVED:
        bcd.status = BCDStatus.REVIEW

    bcd.is_active = True
    bcd.locked_by = None
    bcd.locked_at = None
    await db.commit()
    await db.refresh(bcd)
    return bcd
