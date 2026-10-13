"""Schemas de autenticación."""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
    user_id: int
    branch_id: int | None = None
    expires_in_minutes: int


class UserMe(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    branch_id: int | None = None
