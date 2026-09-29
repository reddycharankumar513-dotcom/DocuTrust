from app.schemas.chat import Source
from app.vectorstore.chroma import RetrievedChunk


class CitationAgent:
    def run(self, *, documents: list[RetrievedChunk], limit: int = 6) -> list[Source]:
        sources: list[Source] = []
        seen: set[tuple[str, int | None]] = set()

        for document in documents:
            filename = str(document.metadata.get("filename") or "Unknown source")
            page = document.metadata.get("page")
            page_number = int(page) if isinstance(page, int | float | str) and str(page).isdigit() else None
            key = (filename, page_number)
            if key in seen:
                continue
            seen.add(key)

            snippet = " ".join(document.text.split())[:280]
            sources.append(
                Source(
                    source_id=document.id,
                    filename=filename,
                    page=page_number,
                    snippet=snippet,
                    score=round(document.score, 4),
                )
            )
            if len(sources) >= limit:
                break
        return sources
