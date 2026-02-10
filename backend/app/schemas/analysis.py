from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_id: int
    summary: str
    created_at: datetime


class ReportResponse(BaseModel):
    filename: str
    size_bytes: int
