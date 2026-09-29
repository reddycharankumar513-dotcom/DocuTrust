import math
import re

from app.config import settings
from app.vectorstore.chroma import RetrievedChunk


class GradingAgent:
    def __init__(self) -> None:
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(settings.reranker_model)
        except Exception:
            self._model = False
        return self._model

    async def run(self, *, question: str, documents: list[RetrievedChunk]) -> tuple[float, list[RetrievedChunk]]:
        if not documents:
            return 0.0, []

        model = self._load_model()
        if model:
            pairs = [(question, document.text) for document in documents]
            raw_scores = model.predict(pairs)
            scored = [
                RetrievedChunk(
                    id=document.id,
                    text=document.text,
                    metadata=document.metadata,
                    score=self._sigmoid(float(score)),
                )
                for document, score in zip(documents, raw_scores, strict=False)
            ]
        else:
            scored = [
                RetrievedChunk(
                    id=document.id,
                    text=document.text,
                    metadata=document.metadata,
                    score=max(document.score, self._lexical_score(question, document.text)),
                )
                for document in documents
            ]

        ranked = sorted(scored, key=lambda document: document.score, reverse=True)
        top_scores = [document.score for document in ranked[:3]]
        average_score = sum(top_scores) / len(top_scores)
        return round(average_score, 4), ranked

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-value))

    @staticmethod
    def _lexical_score(question: str, text: str) -> float:
        question_terms = set(re.findall(r"[a-zA-Z0-9]{3,}", question.lower()))
        text_terms = set(re.findall(r"[a-zA-Z0-9]{3,}", text.lower()))
        if not question_terms:
            return 0.0
        return len(question_terms & text_terms) / len(question_terms)
