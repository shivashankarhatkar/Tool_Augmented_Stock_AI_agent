"""Loads raw text out of PDF books in the configured books directory."""
import os
from typing import Dict
from pypdf import PdfReader
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


# def load_pdfs(books_dir: str = None) -> Dict[str, str]:
#     """Return {filename: full_text} for every PDF found in books_dir."""
#     books_dir = books_dir or settings.books_dir
#     texts: Dict[str, str] = {}

#     if not os.path.isdir(books_dir):
#         logger.warning(f"Books directory '{books_dir}' does not exist.")
#         return texts

#     for fname in sorted(os.listdir(books_dir)):
#         if not fname.lower().endswith(".pdf"):
#             continue
#         path = os.path.join(books_dir, fname)
#         try:
#             reader = PdfReader(path)
#             pages_text = []
#             for page in reader.pages:
#                 page_text = page.extract_text() or ""
#                 pages_text.append(page_text)
#             texts[fname] = "\n".join(pages_text)
#             logger.info(f"Loaded '{fname}' ({len(reader.pages)} pages).")
#         except Exception as exc:  # noqa: BLE001
#             logger.error(f"Failed to load PDF '{fname}': {exc}")

#     return texts

def load_pdfs(books_dir: str = None) -> Dict[str, str]:
    """
    Load all PDF files from the specified directory and extract their text.

    Args:
        books_dir: Directory containing PDF documents. If not provided,
                   the default directory from application settings is used.

    Returns:
        A dictionary mapping each PDF filename to its extracted text.
    """
    # Use the configured books directory if no path is provided.
    books_dir = books_dir or settings.books_dir
    texts: Dict[str, str] = {}

    # Return an empty dictionary if the directory does not exist.
    if not os.path.isdir(books_dir):
        logger.warning(f"Books directory '{books_dir}' does not exist.")
        return texts

    # Iterate through all PDF files in the directory.
    for fname in sorted(os.listdir(books_dir)):
        if not fname.lower().endswith(".pdf"):
            continue

        path = os.path.join(books_dir, fname)

        try:
            # Read the PDF file.
            reader = PdfReader(path)
            pages_text = []

            # Extract text from each page.
            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages_text.append(page_text)

            # Store the complete document text using the filename as the key.
            texts[fname] = "\n".join(pages_text)

            logger.info(f"Loaded '{fname}' ({len(reader.pages)} pages).")

        except Exception as exc:  # noqa: BLE001
            # Log the error and continue processing the remaining PDFs.
            logger.error(f"Failed to load PDF '{fname}': {exc}")

    return texts