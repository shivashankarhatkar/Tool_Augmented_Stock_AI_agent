"""Schema representing retrieval results from the vector store."""
from typing import List
from pydantic import BaseModel


class RAGChunk(BaseModel):
    text: str
    source: str
    score: float


class RAGResult(BaseModel):
    query: str
    chunks: List[RAGChunk] = []

    @property
    def context_text(self) -> str:
        return "\n\n---\n\n".join(
            f"(Source: {c.source})\n{c.text}" for c in self.chunks
        )
