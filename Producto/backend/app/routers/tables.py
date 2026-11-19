"""Gestión de mesas y mapa de mesas."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_admin
from app.models.table import RestaurantTable
from app.models.user import User, UserRole
from app.schemas.table import TableCreate, TableResponse, TableUpdate
from app.utils.algorithms import backtrack_assign

router = APIRouter()


class AssignTablesRequest(BaseModel):
    table_ids: List[int]
    mesero_ids: List[int]


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


@router.post("/assign", dependencies=[Depends(get_current_user)])
def assign_tables(request: AssignTablesRequest, db: Session = Depends(get_db)):
    tables = db.query(RestaurantTable).filter(RestaurantTable.id.in_(request.table_ids)).all()
    meseros = db.query(User).filter(User.id.in_(request.mesero_ids), User.role == UserRole.MESERO).all()
    result = backtrack_assign(tables, meseros)
    if result is None:
        raise HTTPException(status_code=400, detail="No valid assignment found (backtracking)")
    return [{"table_id": t.id, "table_number": t.number, "mesero_id": m.id, "mesero_name": m.full_name} for t, m in result]
