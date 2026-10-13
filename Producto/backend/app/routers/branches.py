"""Gestión de sedes. Lectura para usuarios autenticados; edición solo Administrador."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_admin
from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchResponse, BranchUpdate

router = APIRouter()


@router.get("/", response_model=list[BranchResponse])
def list_branches(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Branch).order_by(Branch.id).all()


@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_branch(request: BranchCreate, db: Session = Depends(get_db)):
    if db.query(Branch).filter(Branch.name == request.name).first():
        raise HTTPException(status_code=400, detail="Branch name already exists")
    branch = Branch(**request.model_dump())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.put("/{branch_id}", response_model=BranchResponse, dependencies=[Depends(require_admin)])
def update_branch(branch_id: int, request: BranchUpdate, db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(branch, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not update branch (duplicate name)")
    db.refresh(branch)
    return branch
