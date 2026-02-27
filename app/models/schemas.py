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
    token_type: str = 'bearer'


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
