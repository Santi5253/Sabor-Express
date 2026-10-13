"""Servicio de autenticación: validación de credenciales y bloqueo por intentos."""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.utils.security import create_access_token, verify_password


class AuthError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def authenticate(db: Session, email: str, password: str, remember: bool = False) -> dict:
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        if user:
            user.login_attempts = (user.login_attempts or 0) + 1
            if user.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.LOCKOUT_DURATION_MINUTES
                )
            db.commit()
        raise AuthError(401, "Invalid credentials")

    if not user.is_active:
        raise AuthError(403, "Account is inactive")

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise AuthError(423, f"Account locked. Try again after {user.locked_until}")

    user.login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()

    token, minutes = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role.value,
            "name": user.full_name,
            "branch_id": user.branch_id,
        },
        remember=remember,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.value,
        "name": user.full_name,
        "user_id": user.id,
        "branch_id": user.branch_id,
        "expires_in_minutes": minutes,
    }
