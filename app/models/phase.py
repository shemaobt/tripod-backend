from datetime import datetime

from pydantic import BaseModel, Field


class PhaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)


class PhaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    status: str | None = Field(default=None, max_length=20)


class PhaseResponse(BaseModel):
    id: str
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    project_ids: list[str] | None = None

    model_config = {"from_attributes": True}


class DependencyCreate(BaseModel):
    depends_on_id: str


class PhaseDependencyResponse(BaseModel):
    id: str
    phase_id: str
    depends_on_id: str

    model_config = {"from_attributes": True}


class AttachPhaseRequest(BaseModel):
    phase_id: str
