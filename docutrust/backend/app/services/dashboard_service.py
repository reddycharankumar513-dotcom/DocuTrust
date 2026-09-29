from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.collections import CHAT_HISTORY_COLLECTION, DOCUMENTS_COLLECTION, INTERACTION_LOGS_COLLECTION
from app.schemas.dashboard import DashboardOut, RecentActivity


class DashboardService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db

    async def get_dashboard(self, *, user: dict) -> DashboardOut:
        user_id = str(user["_id"])
        total_documents = await self.db[DOCUMENTS_COLLECTION].count_documents({"user_id": user_id})
        total_chats = await self.db[CHAT_HISTORY_COLLECTION].count_documents({"user_id": user_id})

        log_cursor = self.db[INTERACTION_LOGS_COLLECTION].find({"user_id": user_id}).sort("timestamp", -1).limit(100)
        scores: list[float] = []
        web_search_count = 0
        log_count = 0
        async for log in log_cursor:
            log_count += 1
            scores.append(float(log.get("retrieval_score", 0.0)))
            if log.get("web_search_used"):
                web_search_count += 1

        recent_activity = await self._recent_activity(user_id)
        average_score = round(sum(scores) / len(scores), 4) if scores else 0.0
        web_usage = round((web_search_count / log_count) * 100, 2) if log_count else 0.0

        return DashboardOut(
            total_documents=total_documents,
            total_chats=total_chats,
            average_retrieval_score=average_score,
            web_search_usage_percent=web_usage,
            recent_activity=recent_activity,
        )

    async def _recent_activity(self, user_id: str) -> list[RecentActivity]:
        activity: list[RecentActivity] = []

        document_cursor = self.db[DOCUMENTS_COLLECTION].find({"user_id": user_id}).sort("upload_time", -1).limit(4)
        async for document in document_cursor:
            activity.append(
                RecentActivity(
                    id=str(document["_id"]),
                    kind="document",
                    title=f"Uploaded {document.get('filename', 'document')}",
                    timestamp=document.get("upload_time", datetime.now(UTC)),
                )
            )

        chat_cursor = self.db[CHAT_HISTORY_COLLECTION].find({"user_id": user_id}).sort("timestamp", -1).limit(4)
        async for chat in chat_cursor:
            activity.append(
                RecentActivity(
                    id=str(chat["_id"]),
                    kind="chat",
                    title=chat.get("question", "Asked a question")[:120],
                    timestamp=chat.get("timestamp", datetime.now(UTC)),
                )
            )

        return sorted(activity, key=lambda item: item.timestamp, reverse=True)[:6]
