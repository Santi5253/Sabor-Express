"""Schemas de Pedidos e Ítems."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1, le=99)
    notes: str | None = Field(None, max_length=200)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float
    notes: str | None = None


class OrderCreate(BaseModel):
    table_id: int
    guests: int = Field(1, ge=1, le=99)
    items: list[OrderItemAdd] = []


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: OrderStatus
    table_id: int
    waiter_id: int
    branch_id: int
    total: float
    igv: float
    guests: int
    opened_at: datetime
    closed_at: datetime | None = None
    items: list[OrderItemResponse] = []
