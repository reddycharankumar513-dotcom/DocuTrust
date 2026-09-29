from datetime import datetime

from pydantic import BaseModel


class DashboardMetric(BaseModel):
    label: str
    value: int | float | str
    delta: str | None = None


class RecentActivity(BaseModel):
    id: str
    kind: str
    title: str
    timestamp: datetime


class DashboardOut(BaseModel):
    total_documents: int
    total_chats: int
    average_retrieval_score: float
    web_search_usage_percent: float
    recent_activity: list[RecentActivity]
