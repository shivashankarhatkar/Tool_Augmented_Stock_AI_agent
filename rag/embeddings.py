"""Embedding model wrapper. Uses a local sentence-transformers model (no API key needed)."""
from typing import List
from sentence_transformers import SentenceTransformer
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_model_cache = {}


class EmbeddingModel:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        if self.model_name not in _model_cache:
            logger.info(f"Loading embedding model '{self.model_name}'...")
            _model_cache[self.model_name] = SentenceTransformer(self.model_name)
        self._model = _model_cache[self.model_name]

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_one(self, text: str) -> List[float]:
        return self.embed([text])[0]
