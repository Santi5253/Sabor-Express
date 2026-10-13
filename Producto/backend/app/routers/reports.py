"""Reportes operativos (solo Administrador): generación y exportación a Excel."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import require_admin
from app.schemas.report import ReportFilter, ReportResponse
from app.services.report_service import generate_report
from app.utils.excel_export import build_report_xlsx

router = APIRouter(dependencies=[Depends(require_admin)])


@router.post("/generate", response_model=ReportResponse)
def generate(request: ReportFilter, db: Session = Depends(get_db)):
    if request.date_from > request.date_to:
        raise HTTPException(status_code=400, detail="'From' date cannot be later than 'To' date")
    return generate_report(db, request.branch_id, request.date_from, request.date_to)


@router.get("/export")
def export(
    branch_id: int,
    date_from: date,
    date_to: date,
    db: Session = Depends(get_db),
):
    if date_from > date_to:
        raise HTTPException(status_code=400, detail="'From' date cannot be later than 'To' date")
    report = generate_report(db, branch_id, date_from, date_to)
    content = build_report_xlsx(report)
    filename = f"SaborExpress_Report_{date_from}_to_{date_to}.xlsx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
