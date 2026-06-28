"""Persistent Chroma vector store wrapper for the investing-books collection."""
from typing import Dict, List, Optional
import chromadb
from config.settings import settings
from utils.logger import get_logger
from utils.exceptions import RAGError

logger = get_logger(__name__)


class ChromaVectorStore:
    def __init__(self, persist_path: str = None, collection_name: str = None):
        self.persist_path = persist_path or settings.chroma_db_path
        self.collection_name = collection_name or settings.rag_collection_name
        self._client = chromadb.PersistentClient(path=self.persist_path)
        self._collection = self._client.get_or_create_collection(name=self.collection_name)

    def add(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
    ) -> None:
        if not ids:
            return
        self._collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

    # def query(self, query_embedding: List[float], top_k: int = 4) -> List[Dict]:
    #     try:
    #         result = self._collection.query(query_embeddings=[query_embedding], n_results=top_k)
    #     except Exception as exc:  # noqa: BLE001
    #         raise RAGError(f"Chroma query failed: {exc}") from exc

    #     docs = result.get("documents", [[]])[0]
    #     metas = result.get("metadatas", [[]])[0]
    #     distances = result.get("distances", [[]])[0]

    #     out = []
    #     for doc, meta, dist in zip(docs, metas, distances):
    #         out.append({"text": doc, "source": meta.get("source", "unknown"), "score": 1 - dist})
    #     return out


    def query(self, query_embedding: List[float], top_k: int = 4) -> List[Dict]:
        """Perform a similarity search in the Chroma vector database.

        Args:
        query_embedding: Embedding vector generated from the user's query.
        top_k: Maximum number of similar documents to retrieve.

        Returns:
            A list of dictionaries containing:
        - text   : Retrieved document content.
        - source : Source file/document of the retrieved chunk.
        - score  : Similarity score (higher is better).
        """
        try:
        # Search the vector database for the most similar document chunks.
            result = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
        except Exception as exc:  # noqa: BLE001
        # Wrap any ChromaDB exception in a project-specific exception.
            raise RAGError(f"Chroma query failed: {exc}") from exc

    # Extract the returned documents, metadata, and similarity distances.
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        out = []

    # Combine each retrieved document with its metadata and similarity score.
        for doc, meta, dist in zip(docs, metas, distances):
            out.append(
            {
                "text": doc,
                "source": meta.get("source", "unknown"),
                # Convert distance into a similarity score.
                "score": 1 - dist,
            }
        )

        return out

    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(name=self.collection_name)
