"""Gestión de proveedores (solo Administrador)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_admin
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderResponse, ProviderUpdate

router = APIRouter()


@router.get("/", response_model=list[ProviderResponse])
def list_providers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Provider).order_by(Provider.id).all()


@router.post("/", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_provider(request: ProviderCreate, db: Session = Depends(get_db)):
    if db.query(Provider).filter(Provider.nit == request.nit).first():
        raise HTTPException(status_code=400, detail="Provider NIT already exists")
    provider = Provider(**request.model_dump())
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.put("/{provider_id}", response_model=ProviderResponse, dependencies=[Depends(require_admin)])
def update_provider(provider_id: int, request: ProviderUpdate, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(provider, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not update provider (duplicate NIT)")
    db.refresh(provider)
    return provider
