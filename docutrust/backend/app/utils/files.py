import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import settings


FILENAME_PATTERN = re.compile(r"[^a-zA-Z0-9_.-]+")


def ensure_storage_dirs() -> None:
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.chroma_path.mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str) -> str:
    cleaned = FILENAME_PATTERN.sub("_", Path(filename).name).strip("._")
    return cleaned or f"document-{uuid4().hex}.pdf"


async def read_pdf_upload(file: UploadFile) -> bytes:
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF files are supported")

    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"PDF exceeds {settings.max_upload_size_mb} MB limit",
        )
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not a valid PDF")

    return content


def write_user_file(user_id: str, filename: str, content: bytes) -> Path:
    user_dir = settings.upload_path / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    path = user_dir / f"{uuid4().hex}-{safe_filename(filename)}"
    path.write_bytes(content)
    return path
