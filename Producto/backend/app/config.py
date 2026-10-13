"""Configuración central del proyecto (SaborExpress API)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos (PostgreSQL en producción, SQLite como fallback de desarrollo)
    DATABASE_URL: str = "sqlite:///./saborexpress.db"

    # Seguridad
    SECRET_KEY: str = "saborexpress-dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3
    REMEMBER_TOKEN_EXPIRE_DAYS: int = 7

    # Reglas de negocio
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    MAX_TRANSACTION_SECONDS: int = 2
    MAX_CONCURRENT_USERS: int = 20

    # CORS
    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
