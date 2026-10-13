"""Modelo de Pagos (tabla payments)."""
import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import value_enum


class PaymentMethod(str, enum.Enum):
    CASH = "Cash"
    DEBIT_CARD = "Debit Card"
    CREDIT_CARD = "Credit Card"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    method = Column(value_enum(PaymentMethod, "payment_method"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    amount_given = Column(Numeric(10, 2), nullable=True)
    change = Column(Numeric(10, 2), nullable=True)
    last_four_digits = Column(String(4), nullable=True)
    authorization_number = Column(String(20), nullable=True)
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="payment")
    cashier = relationship("User")
