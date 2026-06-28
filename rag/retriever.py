"""Retriever: embeds a query and fetches the top-k relevant chunks from Chroma."""
from rag.embeddings import EmbeddingModel
from rag.vector_store import ChromaVectorStore
from schemas.rag_result import RAGResult, RAGChunk
from utils.exceptions import RAGError
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class Retriever:
    def __init__(self):
        self._embedder = EmbeddingModel()
        self._store = ChromaVectorStore()

    def retrieve(self, query: str, top_k: int = None) -> RAGResult:
        top_k = top_k or settings.rag_top_k
        try:
            if self._store.count() == 0:
                logger.warning(
                    "Vector store is empty. Run `python -m rag.ingest` after adding PDFs to data/books/."
                )
                return RAGResult(query=query, chunks=[])

            query_embedding = self._embedder.embed_one(query)
            raw_results = self._store.query(query_embedding, top_k=top_k)
            chunks = [RAGChunk(text=r["text"], source=r["source"], score=r["score"]) for r in raw_results]
            return RAGResult(query=query, chunks=chunks)
        except Exception as exc:  # noqa: BLE001
            raise RAGError(f"Retrieval failed: {exc}") from exc
