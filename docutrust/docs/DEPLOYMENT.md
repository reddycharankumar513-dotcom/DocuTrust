# Deployment Guide

## Container Deployment

1. Copy `.env.example` to `.env`.
2. Set `JWT_SECRET`, model provider keys, and `TAVILY_API_KEY` if web fallback is needed.
3. Run `docker compose up --build -d`.
4. Confirm the backend with `GET /health`.
5. Open the frontend on port `3000`.

## Production Checklist

- Use a managed MongoDB instance or persistent encrypted volume.
- Replace the in-memory rate limiter with Redis-backed limits for multi-replica deployments.
- Move document processing to Celery workers when uploads become large or frequent.
- Store PDFs in object storage instead of container-local disk.
- Put the backend behind TLS and an API gateway.
- Rotate `JWT_SECRET` through a secret manager.
- Restrict CORS origins to production frontend domains.
- Add audit logging for document deletion and admin activity.
- Enable ChromaDB persistent storage backups.

## Scaling Notes

The app is separated so each boundary can scale independently:

- Frontend can be hosted on a static CDN.
- FastAPI can run multiple replicas.
- MongoDB stores users, metadata, history, and interaction logs.
- ChromaDB stores vectorized PDF chunks.
- Redis is included in compose as the next step for distributed rate limits, job queues, and response caching.

## AI Provider Modes

- `LLM_PROVIDER=openai` with `OPENAI_API_KEY` uses the OpenAI chat completion path.
- `LLM_PROVIDER=gemini` with `GEMINI_API_KEY` uses Gemini through LangChain.
- With no provider key, DocuTrust returns extractive cited answers from retrieved evidence.

## Web Fallback

Set `TAVILY_API_KEY` to enable the Web Search Agent. If the key is absent, the agent logs a warning and proceeds with available document evidence.
