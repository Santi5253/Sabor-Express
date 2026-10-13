"""Gestión de mesas y mapa de mesas."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_admin
from app.models.table import RestaurantTable
from app.schemas.table import TableCreate, TableResponse, TableUpdate

router = APIRouter()


@router.get("/", response_model=list[TableResponse])
def list_tables(
    branch_id: int | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(RestaurantTable)
    if branch_id is not None:
        q = q.filter(RestaurantTable.branch_id == branch_id)
    return q.order_by(RestaurantTable.number).all()


@router.post("/", response_model=TableResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_table(request: TableCreate, db: Session = Depends(get_db)):
    if db.query(RestaurantTable).filter(RestaurantTable.number == request.number).first():
        raise HTTPException(status_code=400, detail="Table number already exists")
    table = RestaurantTable(**request.model_dump())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@router.put("/{table_id}", response_model=TableResponse, dependencies=[Depends(require_admin)])
def update_table(table_id: int, request: TableUpdate, db: Session = Depends(get_db)):
    table = db.query(RestaurantTable).filter(RestaurantTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(table, field, value)
    db.commit()
    db.refresh(table)
    return table
