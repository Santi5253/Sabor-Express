"""Gestión de productos. Lectura para roles operativos; edición solo Administrador."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_admin
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.utils.algorithms import binary_search, merge_sort

router = APIRouter()


@router.get("/", response_model=list[ProductResponse])
def list_products(
    branch_id: int | None = None,
    only_available: bool = False,
    sort: str | None = Query(None, description="Ordenar por: name, price, code (Merge Sort)"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Product)
    if branch_id is not None:
        q = q.filter(Product.branch_id == branch_id)
    if only_available:
        q = q.filter(Product.is_available.is_(True))
    products = q.all()
    if sort in {"name", "price", "code"}:
        key = {"name": lambda p: p.name, "price": lambda p: float(p.price), "code": lambda p: p.code}[sort]
        products = merge_sort(products, key)
    else:
        products.sort(key=lambda p: (p.product_type, p.name))
    return products


@router.get("/search", response_model=ProductResponse)
def search_product(
    code: str = Query(..., description="Código exacto del producto (búsqueda binaria)"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    products = sorted(db.query(Product).all(), key=lambda p: p.code)
    found = binary_search(products, lambda p: p.code, code)
    if not found:
        raise HTTPException(status_code=404, detail="Product not found")
    return found


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_product(request: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.code == request.code).first():
        raise HTTPException(status_code=400, detail="Product code already exists")
    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse, dependencies=[Depends(require_admin)])
def update_product(product_id: int, request: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not update product (duplicate code)")
    db.refresh(product)
    return product
