"""Utilidades para columnas Enum que almacenan el VALOR (no el nombre) del enum."""
from sqlalchemy import Enum as SAEnum


def value_enum(enum_cls, name: str | None = None) -> SAEnum:
    """Crea un Enum de SQLAlchemy que persiste el valor del miembro (p. ej. 'Mesero')."""
    return SAEnum(
        enum_cls,
        name=name,
        values_callable=lambda e: [m.value for m in enum_cls],
    )
