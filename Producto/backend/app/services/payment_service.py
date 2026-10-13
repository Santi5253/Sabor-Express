"""Servicio de pagos: efectivo / tarjeta débito / tarjeta crédito (método único)."""
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentMethod
from app.models.table import RestaurantTable, TableStatus
from app.models.user import User


class PaymentError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def create_payment(db: Session, cashier: User, payload) -> Payment:
    order = db.query(Order).filter(Order.id == payload.order_id).first()
    if not order:
        raise PaymentError(404, "Order not found")
    if order.status == OrderStatus.CLOSED:
        raise PaymentError(400, "Order already closed")
    if order.payment is not None:
        raise PaymentError(400, "Order already has a payment (only one method allowed)")

    # Monto a pagar = subtotal de los ítems + IGV (18%)
    total = (Decimal(str(order.total)) + Decimal(str(order.igv))).quantize(Decimal("0.01"))
    change = Decimal("0")

    if payload.method == PaymentMethod.CASH:
        if payload.amount_given is None or Decimal(str(payload.amount_given)) < total:
            raise PaymentError(400, "Insufficient amount")
        change = (Decimal(str(payload.amount_given)) - total).quantize(Decimal("0.01"))
    else:
        if not payload.last_four_digits or not payload.authorization_number:
            raise PaymentError(400, "Card details required (last 4 digits and authorization number)")
        if len(payload.last_four_digits) != 4 or not payload.last_four_digits.isdigit():
            raise PaymentError(400, "Last four digits must be exactly 4 numeric characters")

    payment = Payment(
        order_id=order.id,
        method=payload.method,
        total_amount=total,
        amount_given=payload.amount_given,
        change=change if payload.method == PaymentMethod.CASH else None,
        last_four_digits=payload.last_four_digits,
        authorization_number=payload.authorization_number,
        cashier_id=cashier.id,
    )
    db.add(payment)

    order.status = OrderStatus.CLOSED
    from datetime import datetime

    order.closed_at = datetime.utcnow()

    other_open = (
        db.query(Order)
        .filter(
            Order.table_id == order.table_id,
            Order.status == OrderStatus.OPEN,
            Order.id != order.id,
        )
        .first()
    )
    if not other_open:
        table = db.query(RestaurantTable).filter(RestaurantTable.id == order.table_id).first()
        if table:
            table.status = TableStatus.FREE

    db.commit()
    db.refresh(payment)
    return payment
