from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.org import Organization
from app.services.org.get_organization_by_id import get_organization_by_id


async def get_organization_or_404(db: AsyncSession, organization_id: str) -> Organization:
    org = await get_organization_by_id(db, organization_id)
    if not org:
        raise NotFoundError("Organization not found")
    return org
