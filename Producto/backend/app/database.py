"""Conexión a base de datos con SQLAlchemy 2.0."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# SQLite necesita check_same_thread=False; PostgreSQL usa pool de 20 conexiones
# (coherente con MAX_CONCURRENT_USERS = 20 definido en la arquitectura).
if settings.is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        future=True,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.MAX_CONCURRENT_USERS,
        max_overflow=0,
        pool_pre_ping=True,
        future=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    """Dependencia que entrega una sesión de base de datos por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
