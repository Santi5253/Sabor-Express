"""Servicio de pedidos: construcción, ítems y cálculo de totales (IGV 18%)."""
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.table import RestaurantTable, TableStatus
from app.models.user import User

IGV_RATE = Decimal("0.18")


class OrderError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _next_order_number(db: Session) -> str:
    count = db.query(Order).count()
    return f"PED-{str(count + 1).zfill(5)}"


def recalc_totals(order: Order) -> None:
    total = sum((Decimal(str(i.subtotal)) for i in order.items), Decimal("0"))
    order.total = total
    order.igv = (total * IGV_RATE).quantize(Decimal("0.01"))


def add_item(db: Session, order: Order, product_id: int, quantity: int, notes: str | None) -> None:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise OrderError(404, f"Product {product_id} not found")
    if not product.is_available:
        raise OrderError(400, f"Product '{product.name}' is not available")

    existing = next((i for i in order.items if i.product_id == product_id and (i.notes or "") == (notes or "")), None)
    unit_price = Decimal(str(product.price))
    if existing:
        existing.quantity += quantity
        existing.subtotal = unit_price * existing.quantity
    else:
        order.items.append(
            OrderItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=unit_price * quantity,
                notes=notes,
            )
        )
    db.flush()
    recalc_totals(order)


def create_order(db: Session, waiter: User, table_id: int, guests: int, items: list) -> Order:
    table = db.query(RestaurantTable).filter(RestaurantTable.id == table_id).first()
    if not table:
        raise OrderError(404, "Table not found")

    order = Order(
        order_number=_next_order_number(db),
        table_id=table.id,
        waiter_id=waiter.id,
        branch_id=table.branch_id,
        guests=guests,
        status=OrderStatus.OPEN,
    )
    db.add(order)
    db.flush()

    for item in items:
        add_item(db, order, item.product_id, item.quantity, item.notes)

    table.status = TableStatus.OCCUPIED
    db.commit()
    db.refresh(order)
    return order


def close_order(db: Session, order: Order) -> Order:
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
    db.refresh(order)
    return order
