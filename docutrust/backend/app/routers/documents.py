from fastapi import APIRouter, Depends, File, UploadFile, status

from app.auth.dependencies import get_current_user
from app.database.mongo import get_database
from app.schemas.document import DocumentOut, UploadResult
from app.services.document_service import DocumentService


router = APIRouter(tags=["documents"])


@router.post("/upload", response_model=UploadResult, status_code=status.HTTP_201_CREATED)
async def upload_documents(
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
) -> UploadResult:
    service = DocumentService(get_database())
    documents = await service.upload_pdfs(user=current_user, files=files)
    return UploadResult(documents=documents)


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents(current_user: dict = Depends(get_current_user)) -> list[DocumentOut]:
    service = DocumentService(get_database())
    return await service.list_documents(user=current_user)


@router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)) -> None:
    service = DocumentService(get_database())
    await service.delete_document(user=current_user, document_id=document_id)
