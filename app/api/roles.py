from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_middleware import get_current_user
from app.core.database import get_db
from app.db.models.auth import User
from app.models.schemas import (
    RoleAssignRequest,
    RoleAssignmentResponse,
    RoleCheckResponse,
    RoleRevokeRequest,
)
from app.services import authorization_service

router = APIRouter()


@router.post('/assign', response_model=RoleAssignmentResponse)
async def assign_role(
    payload: RoleAssignRequest,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> RoleAssignmentResponse:
    assignment = await authorization_service.assign_role(
        db,
        actor,
        payload.target_user_id,
        payload.app_key,
        payload.role_key,
    )
    return RoleAssignmentResponse(
        user_id=assignment.user_id,
        app_key=payload.app_key,
        role_key=payload.role_key,
        granted_at=assignment.granted_at,
        revoked_at=assignment.revoked_at,
    )


@router.post('/revoke', response_model=RoleAssignmentResponse)
async def revoke_role(
    payload: RoleRevokeRequest,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> RoleAssignmentResponse:
    assignment = await authorization_service.revoke_role(
        db,
        actor,
        payload.target_user_id,
        payload.app_key,
        payload.role_key,
    )
    return RoleAssignmentResponse(
        user_id=assignment.user_id,
        app_key=payload.app_key,
        role_key=payload.role_key,
        granted_at=assignment.granted_at,
        revoked_at=assignment.revoked_at,
    )


@router.get('/check', response_model=RoleCheckResponse)
async def check_role(
    user_id: str = Query(...),
    app_key: str = Query(...),
    role_key: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RoleCheckResponse:
    allowed = await authorization_service.has_role(db, user_id, app_key, role_key)
    return RoleCheckResponse(allowed=allowed)
