from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Source(BaseModel):
    source_id: str
    filename: str
    page: int | None = None
    snippet: str
    score: float | None = None


class AgentLog(BaseModel):
    step: str
    status: Literal["pending", "running", "completed", "warning", "error"]
    message: str
    timestamp: datetime


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    conversation_id: str | None = None
    top_k: int = Field(default=6, ge=1, le=12)


class FavoriteRequest(BaseModel):
    favorite: bool


class ChatResponse(BaseModel):
    id: str | None = None
    question: str
    answer: str
    sources: list[Source]
    rewritten_query: str | None = None
    retrieval_score: float
    web_search_used: bool
    logs: list[AgentLog]
    timestamp: datetime
    favorite: bool = False
