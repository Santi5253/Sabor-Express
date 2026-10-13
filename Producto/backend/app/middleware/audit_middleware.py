"""Middleware de auditoría / trazabilidad (OWASP #10)."""
from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.database import SessionLocal
from app.models.audit_log import AuditLog
from app.utils.security import decode_token


class AuditMiddleware(BaseHTTPMiddleware):
    """Registra cada operación sobre /api/ en la tabla audit_logs."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith("/api/"):
            user_id = None
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                try:
                    payload = decode_token(auth.split(" ", 1)[1])
                    user_id = int(payload.get("sub", 0)) or None
                except Exception:
                    user_id = None

            # No auditar el login (evita ruido con contraseñas en tránsito)
            if not request.url.path.endswith("/auth/login"):
                db = SessionLocal()
                try:
                    db.add(
                        AuditLog(
                            user_id=user_id,
                            action=request.method,
                            entity=request.url.path,
                            entity_id=None,
                            details=f"status={response.status_code}",
                            ip_address=request.client.host if request.client else None,
                            created_at=datetime.utcnow(),
                        )
                    )
                    db.commit()
                except Exception:
                    db.rollback()
                finally:
                    db.close()

        return response
