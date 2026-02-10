from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CSVUpload, User
from app.schemas.analysis import UploadListItem, UploadListResponse, UploadResponse
from app.services.analysis import summarize_csv
from app.services.reporting import build_executive_pdf
from app.services.subscription import assert_upload_allowed

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        assert_upload_allowed(db, current_user.company_id, current_user.company.subscription_tier)
    except ValueError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc

    content = await file.read()
    try:
        _, summary = summarize_csv(content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to parse CSV: {exc}") from exc

    upload = CSVUpload(
        filename=file.filename,
        uploaded_by_user_id=current_user.id,
        company_id=current_user.company_id,
        analysis_summary=summary,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    return UploadResponse(upload_id=upload.id, summary=summary, created_at=upload.created_at)


@router.get("/uploads", response_model=UploadListResponse)
def list_uploads(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(CSVUpload)
        .where(CSVUpload.company_id == current_user.company_id)
        .order_by(desc(CSVUpload.created_at))
        .limit(25)
    ).all()
    return UploadListResponse(items=[UploadListItem(id=r.id, filename=r.filename, created_at=r.created_at) for r in rows])


@router.get("/report/{upload_id}")
def generate_report(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    upload = db.get(CSVUpload, upload_id)
    if not upload or upload.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Report source not found")

    report_bytes = build_executive_pdf(current_user.company.name, upload.filename, upload.analysis_summary)
    filename = f"executive-report-{upload.id}.pdf"
    return StreamingResponse(
        BytesIO(report_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
