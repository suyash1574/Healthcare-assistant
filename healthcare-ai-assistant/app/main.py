from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.embeddings import ingest_documents
from app.rag import retrieve_context
from app.llm import get_llm_response, compute_confidence
from app.agent import route_question
from app.schemas import (
    AskRequest, AskResponse, Message, HealthResponse, IngestResponse
)
from app.logger import logger

app = FastAPI(title="Healthcare AI Assistant", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


# ── Startup: auto-ingest ─────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    logger.info("Auto-ingesting documents on startup...")
    try:
        result = ingest_documents()
        logger.info(f"Startup ingestion complete: {result['chunks']} chunks")
    except Exception as e:
        logger.warning(f"Startup ingestion skipped (may already exist): {e}")


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        documents_ingested=True
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest():
    """Re-ingest all documents from /data folder into ChromaDB."""
    try:
        result = ingest_documents()
        logger.info(f"Manual ingestion complete: {result['chunks']} chunks")
        return IngestResponse(
            message="Ingestion complete",
            chunks=result["chunks"]
        )
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Main RAG endpoint.
    Routes to appointment tool or LangChain RAG pipeline based on question type.

    Sample request:  { "question": "Can a patient request a medication refill through telehealth?" }
    Sample response: { "answer": "...", "sources": [...], "confidence": "high", "routed_to": "rag" }
    """
    try:
        logger.info(f"Received question: {request.question}")

        # Step 1: Agent routes the question
        routing = route_question(request.question)

        # Step 2a: Appointment tool path
        if routing["type"] == "appointment":
            data = routing["data"]
            slot_list = "\n".join(f"- {s}" for s in data["available_slots"])
            answer = (
                f"I can check mock appointment availability. "
                f"Available slots for **{data['department']}** department"
                f"{' on ' + data['date_requested'] if data['date_requested'] != 'Any available' else ''}:\n\n"
                f"{slot_list}\n\n"
                f"Please contact our reception to confirm your booking."
            )
            logger.info(f"Appointment tool response for department: {data['department']}")
            return AskResponse(
                answer=answer,
                sources=[],
                confidence="high",
                routed_to="appointment"
            )

        # Step 2b: RAG pipeline path
        history = [{"role": m.role, "content": m.content} for m in (request.history or [])]
        contexts, sources = retrieve_context(request.question)

        if not contexts:
            logger.warning("No relevant context found in knowledge base")
            return AskResponse(
                answer="I could not find this information in the provided documents.",
                sources=[],
                confidence="none",
                routed_to="rag"
            )

        context_str = "\n\n".join(contexts)
        answer = get_llm_response(context_str, request.question, history)
        confidence = compute_confidence(sources)

        logger.info(f"RAG response generated — {len(sources)} source(s), confidence={confidence}")
        return AskResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            routed_to="rag"
        )

    except Exception as e:
        logger.error(f"Error in /ask: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
