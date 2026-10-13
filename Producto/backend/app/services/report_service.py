"""Servicio de reportes: ventas por rango de fechas y sede, desglose por método de pago."""
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.payment import Payment


def generate_report(db: Session, branch_id: int, date_from: date, date_to: date) -> dict:
    start = datetime.combine(date_from, time.min)
    end = datetime.combine(date_to, time.max)

    orders = (
        db.query(Order)
        .filter(
            Order.branch_id == branch_id,
            Order.created_at >= start,
            Order.created_at <= end,
            Order.status == OrderStatus.CLOSED,
        )
        .all()
    )

    order_ids = [o.id for o in orders]
    total_sales = float(
        sum((Decimal(str(o.total)) + Decimal(str(o.igv)) for o in orders), Decimal("0"))
    )
    total_igv = float(sum((Decimal(str(o.igv)) for o in orders), Decimal("0")))
    total_orders = len(orders)
    avg_ticket = round(total_sales / total_orders, 2) if total_orders else 0.0

    breakdown = []
    if order_ids:
        rows = (
            db.query(Payment.method, func.count(Payment.id), func.sum(Payment.total_amount))
            .filter(Payment.order_id.in_(order_ids))
            .group_by(Payment.method)
            .all()
        )
        breakdown = [
            {"method": r[0].value, "count": int(r[1]), "total": float(r[2] or 0)}
            for r in rows
        ]

    return {
        "branch_id": branch_id,
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "avg_ticket": avg_ticket,
        "igv_total": round(total_igv, 2),
        "breakdown": breakdown,
        "date_from": str(date_from),
        "date_to": str(date_to),
    }
