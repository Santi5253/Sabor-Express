"""Seguridad: hashing de contraseñas (bcrypt) y tokens JWT."""
from datetime import datetime, timedelta

import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(data: dict, remember: bool = False) -> tuple[str, int]:
    """Crea un JWT. Retorna (token, minutos_de_vigencia)."""
    minutes = (
        settings.REMEMBER_TOKEN_EXPIRE_DAYS * 24 * 60
        if remember
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    payload.update({"exp": expire, "iat": datetime.utcnow()})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, minutes


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
