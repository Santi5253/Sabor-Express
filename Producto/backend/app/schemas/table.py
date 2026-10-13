"""Schemas de Mesas."""
from pydantic import BaseModel, ConfigDict, Field

from app.models.table import TableStatus


class TableBase(BaseModel):
    number: int = Field(..., ge=1)
    capacity: int = Field(..., ge=1, le=99)
    status: TableStatus = TableStatus.FREE
    branch_id: int


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    number: int | None = Field(None, ge=1)
    capacity: int | None = Field(None, ge=1, le=99)
    status: TableStatus | None = None
    branch_id: int | None = None


class TableResponse(TableBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
