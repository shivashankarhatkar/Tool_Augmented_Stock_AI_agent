"""Ingestion pipeline: load PDFs -> chunk -> embed -> store in Chroma.

Run directly:  python -m rag.ingest
"""
from rag.loader import load_pdfs
from rag.chunker import chunk_text
from rag.embeddings import EmbeddingModel
from rag.vector_store import ChromaVectorStore
from utils.logger import get_logger
from config.logging_config import setup_logging

logger = get_logger(__name__)

# Ingest the books into the vector db
def ingest_books(reset: bool = False) -> int:
    """Run the full ingestion pipeline. Returns number of chunks indexed."""
    store = ChromaVectorStore()
    if reset:
        logger.info("Resetting existing collection before ingest.")
        store.reset()
    # Returns the text by loading the pdf in the forms of dictionary as {"filename" : "text"}
    book_texts = load_pdfs()
    if not book_texts:
        logger.warning(
            "No PDFs found in the books directory. Place .pdf files in data/books/ and re-run."
        )
        return 0
    # converts the text into list of embeddings
    embedder = EmbeddingModel()
    total_chunks = 0

    for filename, text in book_texts.items():
        chunks = chunk_text(text, chunk_size=800, overlap=100)
        if not chunks:
            continue
        embeddings = embedder.embed(chunks)
        ids = [f"{filename}::chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        # add the embeddings to the vector store
        store.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
        total_chunks += len(chunks)
        logger.info(f"Indexed {len(chunks)} chunks from '{filename}'.")

    logger.info(f"Ingestion complete. Total chunks indexed: {total_chunks}.")
    return total_chunks


if __name__ == "__main__":
    setup_logging()
    ingest_books(reset=False)
