"""Punto de entrada de la API SaborExpress (FastAPI)."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.middleware.audit_middleware import AuditMiddleware
from app.routers import (
    auth,
    branches,
    orders,
    payments,
    products,
    providers,
    reports,
    tables,
    users,
)

app = FastAPI(
    title="SaborExpress API",
    version="1.0.0",
    description="Sistema de Gestión de Pedidos — Restaurante SaborExpress (NovaTech Soluciones IT S.A.S)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

# --- API v1 ---
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/admin/users", tags=["Users"])
app.include_router(branches.router, prefix="/api/v1/admin/branches", tags=["Branches"])
app.include_router(products.router, prefix="/api/v1/admin/products", tags=["Products"])
app.include_router(providers.router, prefix="/api/v1/admin/providers", tags=["Providers"])
app.include_router(tables.router, prefix="/api/v1/tables", tags=["Tables"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "SaborExpress API", "version": "1.0.0"}


# --- Front-end estático (Vista) ---
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return RedirectResponse(url="/docs")
