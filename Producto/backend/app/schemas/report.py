"""Schemas de Reportes."""
from datetime import date

from pydantic import BaseModel


class ReportFilter(BaseModel):
    branch_id: int
    date_from: date
    date_to: date


class PaymentBreakdown(BaseModel):
    method: str
    count: int
    total: float


class ReportResponse(BaseModel):
    total_sales: float
    total_orders: int
    avg_ticket: float
    igv_total: float
    breakdown: list[PaymentBreakdown]
    date_from: date
    date_to: date
