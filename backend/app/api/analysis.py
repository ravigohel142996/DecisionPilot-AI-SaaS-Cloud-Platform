from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CSVUpload, User
from app.schemas.analysis import UploadResponse
from app.services.analysis import summarize_csv
from app.services.reporting import build_executive_pdf

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    _, summary = summarize_csv(content)

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
