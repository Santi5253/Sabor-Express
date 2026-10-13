"""Schemas de Usuarios."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    full_name: str = Field(..., max_length=100)
    email: EmailStr
    role: UserRole
    phone: str | None = Field(None, max_length=20)
    branch_id: int | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    role: UserRole | None = None
    phone: str | None = Field(None, max_length=20)
    branch_id: int | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8, max_length=72)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_login: datetime | None = None
    created_at: datetime | None = None
