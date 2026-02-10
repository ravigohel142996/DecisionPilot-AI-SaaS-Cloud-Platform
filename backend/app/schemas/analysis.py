from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_id: int
    summary: str
    created_at: datetime


codex/build-saas-version-of-decisionpilot-ai-oqeah7
class UploadListItem(BaseModel):
    id: int
    filename: str
    created_at: datetime


class UploadListResponse(BaseModel):
    items: list[UploadListItem]
=======
class ReportResponse(BaseModel):
    filename: str
    size_bytes: int
main