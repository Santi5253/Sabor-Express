"""Modelo de Mesas (tabla tables)."""
import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import value_enum


class TableStatus(str, enum.Enum):
    FREE = "Free"
    OCCUPIED = "Occupied"


class RestaurantTable(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(value_enum(TableStatus, "table_status"), default=TableStatus.FREE)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("Branch", back_populates="tables")
    orders = relationship("Order", back_populates="table")
