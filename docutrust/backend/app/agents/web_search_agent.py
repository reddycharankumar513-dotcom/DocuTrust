from app.config import settings
from app.vectorstore.chroma import RetrievedChunk


class WebSearchAgent:
    async def run(self, *, query: str, user_id: str) -> list[RetrievedChunk]:
        if not settings.tavily_api_key:
            return []

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=settings.tavily_api_key)
            response = client.search(query=query, max_results=4, search_depth="advanced")
        except Exception:
            return []

        chunks: list[RetrievedChunk] = []
        for index, result in enumerate(response.get("results", [])):
            content = result.get("content") or result.get("raw_content") or ""
            if not content:
                continue
            chunks.append(
                RetrievedChunk(
                    id=f"web:{index}",
                    text=content[:1800],
                    metadata={
                        "user_id": user_id,
                        "document_id": "web",
                        "filename": result.get("url", "Web result"),
                        "page": None,
                        "source_type": "web",
                    },
                    score=float(result.get("score") or 0.5),
                )
            )
        return chunks
