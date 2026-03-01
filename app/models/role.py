from datetime import datetime

from pydantic import BaseModel


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
