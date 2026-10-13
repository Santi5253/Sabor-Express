"""Dependencias de autenticación y autorización por rol (RBAC)."""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(User.id == int(payload.get("sub", 0))).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    request.state.user_id = user.id
    return user


def require_roles(*roles: UserRole):
    """Genera una dependencia que exige que el usuario tenga uno de los roles dados."""

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return checker


require_admin = require_roles(UserRole.ADMINISTRADOR)
require_mesero = require_roles(UserRole.MESERO, UserRole.ADMINISTRADOR)
require_cajero = require_roles(UserRole.CAJERO, UserRole.ADMINISTRADOR)
require_any = require_roles(
    UserRole.MESERO, UserRole.CAJERO, UserRole.ADMINISTRADOR
)
