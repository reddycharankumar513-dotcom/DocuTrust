import hashlib
import math

from app.config import settings


class EmbeddingProvider:
    """Sentence Transformers embeddings with a deterministic local fallback."""

    def __init__(self) -> None:
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(settings.embedding_model)
        except Exception:
            self._model = False
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        if model:
            vectors = model.encode(texts, normalize_embeddings=True)
            return [vector.tolist() for vector in vectors]
        return [self._hash_embedding(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    @staticmethod
    def _hash_embedding(text: str, dimension: int = 384) -> list[float]:
        vector = [0.0] * dimension
        tokens = text.lower().split()
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
