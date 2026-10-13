"""Schemas de Proveedores."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProviderBase(BaseModel):
    name: str = Field(..., max_length=100)
    nit: str = Field(..., max_length=50)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=200)
    is_active: bool = True


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    nit: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=200)
    is_active: bool | None = None


class ProviderResponse(ProviderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
