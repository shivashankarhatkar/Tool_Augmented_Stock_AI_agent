"""FastAPI application exposing the agent over HTTP."""
from fastapi import FastAPI, HTTPException
from schemas.request import QueryRequest
from schemas.response import QueryResponse
from graphs.workflow import get_workflow
from utils.validators import validate_query
from utils.exceptions import ValidationError, AgentBaseException
from config.logging_config import setup_logging
from utils.logger import get_logger
from fastapi.middleware.cors import CORSMiddleware
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Financial Research Agent",
    description="LangGraph-orchestrated agent combining live financial tools and RAG over investing books.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    try:
        clean_query = validate_query(request.query)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        # Retuens the instance of the workflow() class
        workflow = get_workflow()
        result = workflow.run(clean_query, session_id=request.session_id)
        return result
    except AgentBaseException as exc:
        logger.error(f"Workflow execution failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
