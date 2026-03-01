from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_middleware import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.db.models.auth import User
from app.models.org import (
    OrganizationCreate,
    OrganizationMemberAdd,
    OrganizationMemberResponse,
    OrganizationResponse,
)
from app.services import organization_service

router = APIRouter()


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[OrganizationResponse]:
    orgs = await organization_service.list_organizations(db)
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> OrganizationResponse:
    org = await organization_service.create_organization(db, payload.name, payload.slug)
    return OrganizationResponse.model_validate(org)


@router.get("/slug/{slug}", response_model=OrganizationResponse)
async def get_organization_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> OrganizationResponse:
    org = await organization_service.get_organization_by_slug(db, slug)
    if not org:
        raise NotFoundError("Organization not found")
    return OrganizationResponse.model_validate(org)


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization_by_id(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> OrganizationResponse:
    org = await organization_service.get_organization_or_404(db, organization_id)
    return OrganizationResponse.model_validate(org)


@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_organization_member(
    organization_id: str,
    payload: OrganizationMemberAdd,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> OrganizationMemberResponse:
    await organization_service.get_organization_or_404(db, organization_id)
    member = await organization_service.add_member(
        db, organization_id, payload.user_id, payload.role
    )
    return OrganizationMemberResponse.model_validate(member)
