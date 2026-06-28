"""Splits long document text into overlapping chunks suitable for embedding."""
from typing import List


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Naive whitespace-aware sliding-window chunker.

    chunk_size and overlap are measured in characters (simple and dependency-free;
    swap for a token-based splitter if you need exact token budgets).
    """
    text = " ".join(text.split())  # normalize whitespace
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        # try not to cut mid-word
        if end < n:
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)

    return chunks
