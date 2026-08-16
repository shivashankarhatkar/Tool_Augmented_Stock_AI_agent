# Financial Research Agent

A LangGraph-orchestrated agent that answers financial questions by combining:

1. **Live tools** — Alpha Vantage, Yahoo Finance, NewsAPI, SerpAPI, and a safe calculator.
2. **RAG over investing books** — *The Intelligent Investor*, *One Up On Wall Street*,
   *Common Stocks and Uncommon Profits* (you supply the PDFs).
3. **An LLM router/planner/synthesizer** — OpenAI or Gemini, swappable via config.

A query is routed to one of four paths — `tool`, `rag`, `both`, or `direct` — by the router
node, optionally planned into concrete tool calls, executed, retrieved, and synthesized into
a final cited answer.

``````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````
router → planner → tool → rag → synthesis
   │         │                    ▲
   │         └────────────────────┘ (tool-only route)
   └──────────────────────────────┘ (direct / rag-only routes)
````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````

## 1. Setup

```bash
cd financial_research_agent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure environment variables

Copy `.env.example` to `.env` (already done for you) and fill in the keys you have:

```bash
cp .env.example .env
```

| Variable | Required for | Notes |
|---|---|---|
| `LLM_PROVIDER` | Core agent | `openai` or `gemini` |
| `OPENAI_API_KEY` / `GEMINI_API_KEY` | Core agent | Only need the one matching `LLM_PROVIDER` |
| `ALPHA_VANTAGE_API_KEY` | `alpha_vantage` tool | Free tier at alphavantage.co |
| `NEWS_API_KEY` | `news_api` tool | Free tier at newsapi.org |
| `SERPAPI_API_KEY` | `serpapi` tool | serpapi.com |

`yahoo_finance` and `calculator` need **no API key** and work out of the box.
Any tool without a configured key will fail gracefully with a clear error instead of crashing
the whole request — the agent will report what it couldn't fetch.

## 3. Add books & build the vector index (optional, for RAG)

Drop PDF files into `data/books/`, then run:

```bash
python run.py ingest
```

This chunks, embeds (locally, via `sentence-transformers`, no API key needed), and stores them
in a persistent Chroma DB at `data/chroma_db/`. Re-run any time you add new books — it appends
rather than duplicating existing collections unless you pass `reset=True` in code.

## 4. Run it

**As an API server:**
```bash
python run.py api
# -> http://localhost:8000/health
# -> POST http://localhost:8000/query   {"query": "What is AAPL's current price?"}
```
Interactive docs at `http://localhost:8000/docs`.

**As an interactive CLI:**
```bash
python run.py cli
```

**Directly with uvicorn (with autoreload during development):**
```bash
uvicorn app.main:app --reload --port 8000
```

## 5. Run tests

```bash
pytest -v
```

Tests for tools, chunking, schemas, and routing logic run with no external services.
One end-to-end API test is marked `@pytest.mark.skip` since it requires a live LLM key —
run it manually with `pytest tests/test_api.py -k end_to_end --no-skip` after configuring keys
(or just remove the skip decorator once your `.env` is filled in).

## Project structure

```
financial_research_agent/
├── app/            FastAPI app (HTTP layer)
├── tools/          Pluggable tool implementations + registry
├── rag/            PDF loading, chunking, embeddings, vector store, retrieval
├── llm/            Provider-agnostic LLM clients (OpenAI / Gemini) + response parsing
├── prompts/        All prompt templates (router, planner, synthesis, system)
├── schemas/        Pydantic models + LangGraph state definition
├── graphs/         LangGraph nodes, conditional edges, graph builder, workflow wrapper
├── config/         Settings (.env-backed), constants, logging setup
├── utils/          Logger, custom exceptions, validators, generic helpers
├── data/books/     Drop your investing-book PDFs here
├── data/chroma_db/ Persistent vector store (generated)
├── tests/          Pytest suite
└── run.py          Single entrypoint: api | cli | ingest
```

## Extending it

- **New tool:** subclass `BaseTool` in `tools/`, implement `_run()` and `schema()`, register it
  in `tools/tool_registry.py`. The planner will automatically see it via `all_schemas()`.
- **New LLM provider:** add a client in `llm/` matching the `chat(messages, tools, ...)` interface,
  wire it into `llm/llm_factory.py`.
- **Swap the vector DB:** implement the same `add` / `query` / `count` interface as
  `ChromaVectorStore` in `rag/vector_store.py` (e.g. for pgvector or FAISS) and swap it into
  `rag/retriever.py`.

## Notes on production-readiness

- All tool/LLM/RAG failures raise typed exceptions (`utils/exceptions.py`) that are caught at
  node boundaries — a single failing tool degrades the answer rather than crashing the request.
- API keys are read once via `pydantic-settings` (`config/settings.py`); nothing is hardcoded.
- Retries with exponential backoff wrap all outbound HTTP/LLM calls (`utils/helpers.py`).
- Logging is centralized and configurable via `LOG_LEVEL` (`config/logging_config.py`).
- The calculator tool whitelists characters before evaluating — no arbitrary code execution.
