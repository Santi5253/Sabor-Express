"""Schemas de Pagos."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentMethod


class PaymentCreate(BaseModel):
    order_id: int
    method: PaymentMethod
    amount_given: float | None = Field(None, ge=0)  # solo efectivo
    last_four_digits: str | None = Field(None, min_length=4, max_length=4)  # solo tarjeta
    authorization_number: str | None = Field(None, max_length=20)  # solo tarjeta


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    method: PaymentMethod
    total_amount: float
    amount_given: float | None = None
    change: float | None = None
    last_four_digits: str | None = None
    authorization_number: str | None = None
    cashier_id: int
    created_at: datetime
