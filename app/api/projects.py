from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_middleware import get_current_user
from app.core.database import get_db
from app.core.exceptions import AuthorizationError
from app.db.models.auth import User
from app.models.schemas import (
    ProjectCreate,
    ProjectGrantOrganizationAccess,
    ProjectGrantUserAccess,
    ProjectLocationUpdate,
    ProjectOrganizationAccessResponse,
    ProjectResponse,
    ProjectUserAccessResponse,
)
from app.services import project_service

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    language_id: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    projects = await project_service.list_projects_accessible_to_user(db, user.id)
    if language_id is not None:
        projects = [p for p in projects if p.language_id == language_id]
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProjectResponse:
    project = await project_service.create_project(
        db,
        name=payload.name,
        language_id=payload.language_id,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_display_name=payload.location_display_name,
    )
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    project = await project_service.get_project_or_404(db, project_id)
    allowed = await project_service.can_access_project(db, user.id, project_id)
    if not allowed:
        raise AuthorizationError("You do not have access to this project")
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}/location", response_model=ProjectResponse)
async def update_project_location(
    project_id: str,
    payload: ProjectLocationUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    allowed = await project_service.can_access_project(db, user.id, project_id)
    if not allowed:
        raise AuthorizationError("You do not have access to this project")
    project = await project_service.update_project_location(
        db,
        project_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_display_name=payload.location_display_name,
    )
    return ProjectResponse.model_validate(project)


@router.post(
    "/{project_id}/access/users",
    response_model=ProjectUserAccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def grant_user_access(
    project_id: str,
    payload: ProjectGrantUserAccess,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectUserAccessResponse:
    allowed = await project_service.can_access_project(db, actor.id, project_id)
    if not allowed:
        raise AuthorizationError("You do not have access to this project")
    await project_service.get_project_or_404(db, project_id)
    access = await project_service.grant_user_access(db, project_id, payload.user_id)
    return ProjectUserAccessResponse.model_validate(access)


@router.post(
    "/{project_id}/access/organizations",
    response_model=ProjectOrganizationAccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def grant_organization_access(
    project_id: str,
    payload: ProjectGrantOrganizationAccess,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectOrganizationAccessResponse:
    allowed = await project_service.can_access_project(db, actor.id, project_id)
    if not allowed:
        raise AuthorizationError("You do not have access to this project")
    await project_service.get_project_or_404(db, project_id)
    access = await project_service.grant_organization_access(
        db, project_id, payload.organization_id
    )
    return ProjectOrganizationAccessResponse.model_validate(access)
