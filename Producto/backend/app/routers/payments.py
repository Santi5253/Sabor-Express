"""Pagos: registro y cierre del pedido (cajero)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import require_cajero
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentError, create_payment

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def pay(
    request: PaymentCreate,
    db: Session = Depends(get_db),
    cashier: User = Depends(require_cajero),
):
    try:
        return create_payment(db, cashier, request)
    except PaymentError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
