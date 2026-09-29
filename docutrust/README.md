# DocuTrust

Enterprise Advanced RAG Platform with Automated Self-Correction.

DocuTrust lets authenticated users upload PDFs, index them into ChromaDB, ask grounded questions, watch the corrective RAG agents run, and receive cited answers with source filenames and page numbers.

## Architecture

- Frontend: React, TypeScript, Tailwind CSS, shadcn-style UI primitives, Axios, React Markdown.
- Backend: FastAPI, JWT auth, MongoDB, ChromaDB, PyMuPDF, LangGraph, LangChain text splitters.
- AI pipeline: HuggingFace sentence embeddings, `cross-encoder/ms-marco-MiniLM-L-6-v2` reranking, query rewriting, Tavily web fallback, OpenAI or Gemini answer generation.

## Local Setup

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Manual Development

Backend:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
corepack pnpm install
corepack pnpm run dev
```

MongoDB must be running locally at `mongodb://localhost:27017` unless `MONGODB_URI` is changed.

## API Surface

- `POST /register`
- `POST /login`
- `GET /profile`
- `POST /upload`
- `GET /documents`
- `DELETE /document/{id}`
- `POST /chat`
- `GET /history`
- `GET /dashboard`
- `WS /ws/chat?token=...`

## Corrective RAG Flow

1. Query Node validates and normalizes the question.
2. Retriever Node performs semantic search against ChromaDB.
3. Grading Node reranks chunks with a cross encoder.
4. If retrieval is strong enough, Answer Generator runs directly.
5. If retrieval is weak, Query Rewriter expands the query.
6. Web Search Agent runs Tavily fallback when configured.
7. Answer Generator produces a grounded answer.
8. Citation Agent attaches filenames, page numbers, snippets, and scores.

## Environment

Set at least:

```env
JWT_SECRET=replace-with-a-strong-random-secret
MONGODB_URI=mongodb://localhost:27017
OPENAI_API_KEY=
GEMINI_API_KEY=
TAVILY_API_KEY=
```

Without an LLM API key, the backend returns extractive answers from retrieved chunks so the platform remains testable.

## Security Notes

- JWT authentication protects all document, chat, dashboard, and profile routes.
- Uploads are restricted to PDFs and size limited.
- Mongo queries are scoped by `user_id`.
- Prompt injection phrases are detected and isolated in the workflow logs.
- CORS and basic in-memory rate limiting are enabled.

## Tests

```powershell
.\scripts\test-backend.ps1
.\scripts\test-frontend.ps1
python .\scripts\smoke_backend.py
```

See `docs/SCHEMA.md` and `docs/DEPLOYMENT.md` for operational details.
