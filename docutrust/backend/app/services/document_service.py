from datetime import UTC, datetime

from bson import ObjectId
from fastapi import HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.collections import DOCUMENTS_COLLECTION
from app.rag.splitter import chunk_pages, extract_pdf_pages
from app.schemas.document import DocumentOut
from app.utils.files import read_pdf_upload, write_user_file
from app.utils.object_id import to_object_id
from app.vectorstore.chroma import ChromaVectorStore


class DocumentService:
    def __init__(self, db: AsyncIOMotorDatabase, vectorstore: ChromaVectorStore | None = None) -> None:
        self.db = db
        self.vectorstore = vectorstore or ChromaVectorStore()
        self.collection = db[DOCUMENTS_COLLECTION]

    async def upload_pdfs(self, *, user: dict, files: list[UploadFile]) -> list[DocumentOut]:
        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one PDF is required")

        user_id = str(user["_id"])
        uploaded: list[DocumentOut] = []

        for file in files:
            content = await read_pdf_upload(file)
            path = write_user_file(user_id, file.filename or "document.pdf", content)
            now = datetime.now(UTC)
            record = {
                "user_id": user_id,
                "filename": file.filename or path.name,
                "storage_path": str(path),
                "upload_time": now,
                "chunks_count": 0,
                "status": "processing",
            }
            result = await self.collection.insert_one(record)
            document_id = str(result.inserted_id)

            try:
                pages = extract_pdf_pages(path)
                chunks = chunk_pages(pages)
                if not chunks:
                    raise ValueError("No extractable text found in PDF")
                self.vectorstore.upsert_chunks(
                    user_id=user_id,
                    document_id=document_id,
                    filename=record["filename"],
                    chunks=chunks,
                )
                await self.collection.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"chunks_count": len(chunks), "status": "ready"}},
                )
                record.update({"id": document_id, "chunks_count": len(chunks), "status": "ready"})
            except Exception as exc:
                await self.collection.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"status": "failed", "error": str(exc)}},
                )
                record.update({"id": document_id, "status": "failed"})

            uploaded.append(self._to_out(record))

        return uploaded

    async def list_documents(self, *, user: dict) -> list[DocumentOut]:
        cursor = self.collection.find({"user_id": str(user["_id"])}).sort("upload_time", -1)
        documents = []
        async for record in cursor:
            documents.append(self._to_out(record))
        return documents

    async def delete_document(self, *, user: dict, document_id: str) -> None:
        try:
            object_id = to_object_id(document_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document id") from exc

        record = await self.collection.find_one({"_id": object_id, "user_id": str(user["_id"])})
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        await self.collection.delete_one({"_id": object_id})
        self.vectorstore.delete_document(user_id=str(user["_id"]), document_id=document_id)

    @staticmethod
    def _to_out(record: dict) -> DocumentOut:
        object_id = record.get("id") or record.get("_id")
        return DocumentOut(
            id=str(object_id) if isinstance(object_id, ObjectId) else str(object_id),
            filename=record["filename"],
            upload_time=record["upload_time"],
            chunks_count=int(record.get("chunks_count", 0)),
            status=record.get("status", "ready"),
        )
