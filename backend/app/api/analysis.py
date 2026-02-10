from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CSVUpload, DatasetVersion, User
from app.schemas.analysis import (
    DatasetVersionResponse,
    RealtimeAnalyticsResponse,
    UploadListItem,
    UploadListResponse,
    UploadResponse,
)
from app.services.analysis import build_realtime_metrics, summarize_csv
from app.services.reporting import build_executive_pdf
from app.services.subscription import assert_upload_allowed

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are allowed")

    try:
        assert_upload_allowed(db, current_user.company_id, current_user.company.subscription_tier)
    except ValueError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc

    content = await file.read()
    try:
        df, summary, metadata = summarize_csv(content, file.filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to parse data file: {exc}") from exc

    upload = CSVUpload(
        filename=file.filename,
        uploaded_by_user_id=current_user.id,
        company_id=current_user.company_id,
        analysis_summary=summary,
    )
    db.add(upload)
    db.flush()

    version_label = f"v{upload.id}"
    dataset_version = DatasetVersion(
        company_id=current_user.company_id,
        source_upload_id=upload.id,
        version_label=version_label,
        rows_count=df.shape[0],
        columns_count=df.shape[1],
        metadata_json=metadata,
    )
    db.add(dataset_version)
    db.commit()
    db.refresh(upload)

    return UploadResponse(upload_id=upload.id, summary=summary, created_at=upload.created_at, dataset_version=version_label)


@router.get("/uploads", response_model=UploadListResponse)
def list_uploads(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(CSVUpload).where(CSVUpload.company_id == current_user.company_id).order_by(desc(CSVUpload.created_at)).limit(25)
    ).all()
    return UploadListResponse(items=[UploadListItem(id=r.id, filename=r.filename, created_at=r.created_at) for r in rows])


@router.get("/datasets", response_model=list[DatasetVersionResponse])
def list_dataset_versions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    versions = db.scalars(
        select(DatasetVersion).where(DatasetVersion.company_id == current_user.company_id).order_by(desc(DatasetVersion.created_at))
    ).all()
    return [
        DatasetVersionResponse(
            version_label=v.version_label,
            rows_count=v.rows_count,
            columns_count=v.columns_count,
            metadata=v.metadata_json,
            created_at=v.created_at,
        )
        for v in versions
    ]


@router.get("/realtime", response_model=RealtimeAnalyticsResponse)
def realtime_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    latest = db.scalar(
        select(CSVUpload).where(CSVUpload.company_id == current_user.company_id).order_by(desc(CSVUpload.created_at)).limit(1)
    )
    if not latest:
        raise HTTPException(status_code=404, detail="No dataset available")

    # derive lightweight metrics from stored summary text for quick response
    lines = latest.analysis_summary.splitlines()
    nums = []
    for line in lines:
        for token in line.replace(",", " ").split():
            try:
                nums.append(float(token.split("=")[-1]))
            except ValueError:
                continue

    import pandas as pd

    synthetic = pd.DataFrame({"revenue": nums[:50] or [100, 120, 130], "cost": nums[:50] or [60, 66, 72]})
    metrics = build_realtime_metrics(synthetic)
    return RealtimeAnalyticsResponse(**metrics)


@router.get("/report/{upload_id}")
def generate_report(upload_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    upload = db.get(CSVUpload, upload_id)
    if not upload or upload.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Report source not found")

    report_bytes = build_executive_pdf(current_user.company.name, upload.filename, upload.analysis_summary)
    filename = f"visionpilot-executive-report-{upload.id}.pdf"
    return StreamingResponse(
        BytesIO(report_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
