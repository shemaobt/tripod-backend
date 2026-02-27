from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class HealthResponse(BaseModel):
    status: str


class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    display_name: str | None
    is_active: bool
    is_platform_admin: bool


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class RoleAssignRequest(BaseModel):
    target_user_id: str
    app_key: str
    role_key: str


class RoleRevokeRequest(BaseModel):
    target_user_id: str
    app_key: str
    role_key: str


class RoleAssignmentResponse(BaseModel):
    user_id: str
    app_key: str
    role_key: str
    granted_at: datetime
    revoked_at: datetime | None


class RoleCheckResponse(BaseModel):
    allowed: bool


class MyRoleResponse(BaseModel):
    app_key: str
    role_key: str


class LanguageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=1, max_length=3)


class LanguageResponse(BaseModel):
    id: str
    name: str
    code: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=100)


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrganizationMemberAdd(BaseModel):
    user_id: str
    role: str = Field(default="member", max_length=50)


class OrganizationMemberResponse(BaseModel):
    id: str
    user_id: str
    organization_id: str
    role: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    language_id: str
    latitude: float | None = None
    longitude: float | None = None
    location_display_name: str | None = Field(default=None, max_length=500)


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    language_id: str
    latitude: float | None
    longitude: float | None
    location_display_name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectLocationUpdate(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    location_display_name: str | None = Field(default=None, max_length=500)


class ProjectGrantUserAccess(BaseModel):
    user_id: str


class ProjectGrantOrganizationAccess(BaseModel):
    organization_id: str


class ProjectUserAccessResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    granted_at: datetime

    model_config = {"from_attributes": True}


class ProjectOrganizationAccessResponse(BaseModel):
    id: str
    project_id: str
    organization_id: str
    granted_at: datetime

    model_config = {"from_attributes": True}
