"""Pedidos: creación (mesero), consulta, ítems y cierre (cajero)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_cajero, require_mesero
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderItemAdd, OrderResponse
from app.services.order_service import OrderError, add_item, close_order, create_order

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create(
    request: OrderCreate,
    db: Session = Depends(get_db),
    waiter: User = Depends(require_mesero),
):
    try:
        return create_order(db, waiter, request.table_id, request.guests, request.items)
    except OrderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/{order_id}/items", response_model=OrderResponse)
def add_item_to_order(
    order_id: int,
    request: OrderItemAdd,
    db: Session = Depends(get_db),
    _=Depends(require_mesero),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == OrderStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Cannot modify a closed order")
    try:
        add_item(db, order, request.product_id, request.quantity, request.notes)
        db.commit()
        db.refresh(order)
        return order
    except OrderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/my-active", response_model=list[OrderResponse])
def my_active(db: Session = Depends(get_db), user: User = Depends(require_mesero)):
    return (
        db.query(Order)
        .filter(Order.waiter_id == user.id, Order.status == OrderStatus.OPEN)
        .order_by(Order.created_at.desc())
        .all()
    )


@router.get("/open", response_model=list[OrderResponse])
def open_orders(
    branch_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Order).filter(Order.status == OrderStatus.OPEN)
    target_branch = branch_id or user.branch_id
    if target_branch is not None:
        q = q.filter(Order.branch_id == target_branch)
    return q.order_by(Order.created_at.asc()).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}/close", response_model=OrderResponse)
def close(order_id: int, db: Session = Depends(get_db), _=Depends(require_cajero)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == OrderStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Order already closed")
    return close_order(db, order)
