"""Schemas de Productos."""
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    product_type: str = Field(..., max_length=50)
    provider_id: int
    price: float = Field(..., gt=0)
    is_available: bool = True
    branch_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    code: str | None = Field(None, max_length=50)
    name: str | None = Field(None, max_length=100)
    product_type: str | None = Field(None, max_length=50)
    provider_id: int | None = None
    price: float | None = Field(None, gt=0)
    is_available: bool | None = None
    branch_id: int | None = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
