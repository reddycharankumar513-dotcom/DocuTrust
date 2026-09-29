from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    upload_time: datetime
    chunks_count: int
    status: str


class UploadResult(BaseModel):
    documents: list[DocumentOut]
