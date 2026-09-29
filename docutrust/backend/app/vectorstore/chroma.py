from dataclasses import dataclass
from typing import Any

from app.config import settings
from app.embeddings.huggingface import EmbeddingProvider


@dataclass
class RetrievedChunk:
    id: str
    text: str
    metadata: dict[str, Any]
    score: float


_GLOBAL_MEMORY: list[RetrievedChunk] = []


class ChromaVectorStore:
    def __init__(self, embeddings: EmbeddingProvider | None = None) -> None:
        self.embeddings = embeddings or EmbeddingProvider()
        self._client = None
        self._collection = None

    @property
    def collection(self):
        if self._collection is not None:
            return self._collection

        try:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(settings.chroma_path))
            self._collection = self._client.get_or_create_collection(
                name="docutrust_chunks",
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            self._collection = False
        return self._collection

    def upsert_chunks(self, *, user_id: str, document_id: str, filename: str, chunks: list[dict]) -> None:
        if not chunks:
            return

        ids = [f"{document_id}:{index}" for index, _ in enumerate(chunks)]
        documents = [chunk["text"] for chunk in chunks]
        embeddings = self.embeddings.embed_documents(documents)
        metadatas = [
            {
                "user_id": user_id,
                "document_id": document_id,
                "filename": filename,
                "page": int(chunk.get("page") or 1),
                "chunk_index": index,
            }
            for index, chunk in enumerate(chunks)
        ]

        global _GLOBAL_MEMORY
        for chunk_id, text, metadata in zip(ids, documents, metadatas, strict=False):
            _GLOBAL_MEMORY.append(RetrievedChunk(id=chunk_id, text=text, metadata=metadata, score=1.0))

        collection = self.collection
        if collection:
            try:
                collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
            except Exception:
                pass

    def search(self, *, user_id: str, query: str, top_k: int) -> list[RetrievedChunk]:
        collection = self.collection
        query_embedding = self.embeddings.embed_query(query)

        if collection:
            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where={"user_id": user_id},
                    include=["documents", "metadatas", "distances"],
                )
                chunks: list[RetrievedChunk] = []
                if results and results.get("ids") and results["ids"][0]:
                    for chunk_id, text, metadata, distance in zip(
                        results.get("ids", [[]])[0],
                        results.get("documents", [[]])[0],
                        results.get("metadatas", [[]])[0],
                        results.get("distances", [[]])[0],
                        strict=False,
                    ):
                        score = max(0.0, min(1.0, 1.0 - float(distance)))
                        chunks.append(RetrievedChunk(id=chunk_id, text=text, metadata=metadata or {}, score=score))
                if chunks:
                    return chunks
            except Exception:
                pass

        query_terms = set(query.lower().split())
        scored = []
        for chunk in _GLOBAL_MEMORY:
            if chunk.metadata.get("user_id") != user_id:
                continue
            text_terms = set(chunk.text.lower().split())
            overlap = len(query_terms & text_terms) / max(len(query_terms), 1)
            scored.append(RetrievedChunk(id=chunk.id, text=chunk.text, metadata=chunk.metadata, score=overlap))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

    def delete_document(self, *, user_id: str, document_id: str) -> None:
        global _GLOBAL_MEMORY
        _GLOBAL_MEMORY = [
            chunk for chunk in _GLOBAL_MEMORY
            if not (chunk.metadata.get("user_id") == user_id and chunk.metadata.get("document_id") == document_id)
        ]

        collection = self.collection
        if collection:
            try:
                where = {"$and": [{"user_id": user_id}, {"document_id": document_id}]}
                collection.delete(where=where)
            except Exception:
                pass
