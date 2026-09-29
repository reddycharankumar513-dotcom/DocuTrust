from app.vectorstore.chroma import ChromaVectorStore, RetrievedChunk


class RetrievalAgent:
    def __init__(self, vectorstore: ChromaVectorStore | None = None) -> None:
        self.vectorstore = vectorstore or ChromaVectorStore()

    async def run(self, *, user_id: str, question: str, top_k: int) -> list[RetrievedChunk]:
        return self.vectorstore.search(user_id=user_id, query=question, top_k=top_k)
