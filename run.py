"""Entrypoint script.

Usage:
    python run.py api            # start the FastAPI server (default)
    python run.py cli            # interactive command-line chat loop
    python run.py ingest         # ingest PDFs from data/books/ into the vector store
"""
import sys
from config.logging_config import setup_logging
from config.settings import settings
from utils.logger import get_logger

setup_logging()
logger = get_logger(__name__)


def run_api() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=False)


def run_cli() -> None:
    from graphs.workflow import get_workflow

    workflow = get_workflow()
    print("Financial Research Agent (CLI mode). Type 'exit' to quit.\n")
    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            print("Goodbye.")
            break
        response = workflow.run(query)
        print(f"\nAgent [{response.route}]: {response.answer}")
        if response.sources:
            print(f"Sources: {', '.join(response.sources)}")
        print()


def run_ingest() -> None:
    from rag.ingest import ingest_books

    count = ingest_books()
    print(f"Ingested {count} chunks into the vector store.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"
    if mode == "api":
        run_api()
    elif mode == "cli":
        run_cli()
    elif mode == "ingest":
        run_ingest()
    else:
        print(f"Unknown mode '{mode}'. Use one of: api, cli, ingest")
        sys.exit(1)
