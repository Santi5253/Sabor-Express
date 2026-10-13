"""Schemas de Sedes."""
from pydantic import BaseModel, ConfigDict, Field


class BranchBase(BaseModel):
    name: str = Field(..., max_length=100)
    address: str = Field(..., max_length=200)
    phone: str | None = Field(None, max_length=20)
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    address: str | None = Field(None, max_length=200)
    phone: str | None = Field(None, max_length=20)
    is_active: bool | None = None


class BranchResponse(BranchBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
