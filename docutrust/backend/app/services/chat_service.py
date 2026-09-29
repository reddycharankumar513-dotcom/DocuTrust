import time
from io import BytesIO
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from xml.sax.saxutils import escape

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.collections import CHAT_HISTORY_COLLECTION, INTERACTION_LOGS_COLLECTION
from app.rag.graph import CorrectiveRAGGraph
from app.schemas.chat import AgentLog, ChatRequest, ChatResponse
from app.utils.object_id import to_object_id


class ChatService:
    def __init__(self, db: AsyncIOMotorDatabase, graph: CorrectiveRAGGraph | None = None) -> None:
        self.db = db
        self.graph = graph or CorrectiveRAGGraph()

    async def answer_question(
        self,
        *,
        user: dict,
        request: ChatRequest,
        emit: Callable[[AgentLog], Awaitable[None]] | None = None,
    ) -> ChatResponse:
        logs: list[AgentLog] = []

        async def capture(log: AgentLog) -> None:
            logs.append(log)
            if emit:
                await emit(log)

        started = time.perf_counter()
        state = await self.graph.run(
            user_id=str(user["_id"]),
            question=request.question,
            top_k=request.top_k,
            emit=capture,
        )
        elapsed = time.perf_counter() - started
        timestamp = datetime.now(UTC)

        response = ChatResponse(
            question=state["question"],
            answer=state.get("generation", ""),
            sources=state.get("sources", []),
            rewritten_query=state.get("rewritten_query") or None,
            retrieval_score=float(state.get("retrieval_score", 0.0)),
            web_search_used=bool(state.get("web_search_needed", False)),
            logs=logs,
            timestamp=timestamp,
        )

        history_doc = response.model_dump()
        history_doc["user_id"] = str(user["_id"])
        insert_result = await self.db[CHAT_HISTORY_COLLECTION].insert_one(history_doc)
        response.id = str(insert_result.inserted_id)

        await self.db[INTERACTION_LOGS_COLLECTION].insert_one(
            {
                "user_id": str(user["_id"]),
                "question": response.question,
                "rewritten_query": response.rewritten_query,
                "retrieval_score": response.retrieval_score,
                "web_search_used": response.web_search_used,
                "time_taken": round(elapsed, 4),
                "timestamp": timestamp,
            }
        )
        return response

    async def list_history(self, *, user: dict, limit: int = 25) -> list[ChatResponse]:
        cursor = self.db[CHAT_HISTORY_COLLECTION].find({"user_id": str(user["_id"])}).sort("timestamp", -1).limit(limit)
        items: list[ChatResponse] = []
        async for record in cursor:
            record["id"] = str(record.pop("_id"))
            record.pop("user_id", None)
            items.append(ChatResponse(**record))
        return items

    async def toggle_favorite(self, *, user: dict, chat_id: str, favorite: bool) -> None:
        result = await self.db[CHAT_HISTORY_COLLECTION].update_one(
            {"_id": self._parse_chat_id(chat_id), "user_id": str(user["_id"])},
            {"$set": {"favorite": favorite}},
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    async def export_pdf(self, *, user: dict, chat_id: str) -> bytes:
        record = await self.db[CHAT_HISTORY_COLLECTION].find_one(
            {"_id": self._parse_chat_id(chat_id), "user_id": str(user["_id"])}
        )
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
        except ImportError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PDF export dependency missing") from exc

        buffer = BytesIO()
        document = SimpleDocTemplate(buffer, pagesize=letter, title="DocuTrust Chat Export")
        styles = getSampleStyleSheet()
        story = [
            Paragraph("DocuTrust Chat Export", styles["Title"]),
            Spacer(1, 12),
            Paragraph("Question", styles["Heading2"]),
            Paragraph(escape(record.get("question", "")), styles["BodyText"]),
            Spacer(1, 12),
            Paragraph("Answer", styles["Heading2"]),
            Paragraph(escape(record.get("answer", "")).replace("\n", "<br/>"), styles["BodyText"]),
            Spacer(1, 12),
            Paragraph("Sources", styles["Heading2"]),
        ]
        for source in record.get("sources", []):
            page = f", page {source['page']}" if source.get("page") else ""
            story.append(Paragraph(escape(f"{source.get('filename', 'Source')}{page}"), styles["BodyText"]))

        document.build(story)
        buffer.seek(0)
        return buffer.read()

    @staticmethod
    def _parse_chat_id(chat_id: str):
        try:
            return to_object_id(chat_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat id") from exc
