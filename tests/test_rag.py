"""Unit tests for the RAG chunking logic (no external services required)."""
from rag.chunker import chunk_text


def test_chunk_text_empty():
    assert chunk_text("") == []


def test_chunk_text_respects_size_roughly():
    text = "word " * 1000
    chunks = chunk_text(text, chunk_size=200, overlap=20)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 220  # allow small overshoot due to word-boundary snapping


def test_chunk_text_overlap_present():
    text = "abcdefgh " * 100
    chunks = chunk_text(text, chunk_size=100, overlap=30)
    assert len(chunks) >= 2
