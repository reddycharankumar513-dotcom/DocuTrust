from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.mongo import close_mongo_connection, connect_to_mongo
from app.routers import auth, chat, dashboard, documents
from app.utils.files import ensure_storage_dirs
from app.utils.rate_limit import InMemoryRateLimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage_dirs()
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Enterprise corrective RAG platform with citations and self-correction.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(InMemoryRateLimiter)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)


@app.get("/health", tags=["system"])
@app.get("/api/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok", "service": "docutrust-api"}

