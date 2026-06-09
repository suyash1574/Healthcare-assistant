# Project: Healthcare AI Assistant

## Architecture
The application is a Retrieval-Augmented Generation (RAG) backend API built with FastAPI, integrated with an agentic intent-based router.

### Components & Data Flow:
1. **API Layer (`app/main.py`)**: Exposes FastAPI endpoints (`GET /health`, `POST /ingest`, `POST /ask`).
2. **Agentic Router (`app/agent.py`)**: Checks incoming queries for scheduling/booking intent.
   - If booking/availability intent is detected, it routes to `app/appointment_tool.py` (Mock tool: `check_available_slots`).
   - If informational/RAG intent is detected, it routes to the RAG pipeline.
3. **RAG Pipeline (`app/rag.py` & `app/embeddings.py`)**:
   - Ingestion: Reads documents (`.txt` and `.pdf`) from `data/`, chunks them via `RecursiveCharacterTextSplitter`, creates normalized embeddings via `HuggingFaceEmbeddings` using the model `all-MiniLM-L6-v2`, and stores them in ChromaDB (`vector_store/`).
   - Retrieval: Converts the query to embeddings, queries ChromaDB for the top `k` most similar chunks matching a similarity threshold, and extracts text content and metadata sources.
4. **LLM Generation (`app/llm.py` & `app/prompting.py`)**: Passes retrieved context and user question to the LLM.
   - Uses a priority fallback queue of LLM APIs: Groq (llama-3.3-70b-versatile) -> Nvidia NIM (meta/llama-3.3-70b-instruct) -> OpenRouter free models.
   - Leverages system prompt safety guardrails to avoid direct diagnoses and stay within context.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M1 | Git Repository Cleanup | Remove `pkgs/` and `test-screenshot.png` from tracking, correct `.gitignore`. | None | DONE |
| M2 | E2E Test Suite Creation | Create robust opaque-box test suite across 4 tiers, publish `TEST_READY.md`. | None | IN_PROGRESS |
| M3 | Application Integrity & Fixes | Run tests, fix FastAPI backend, mock tools, frontend connectivity, ensure 100% test pass. | M1, M2 | PLANNED |
| M4 | Documentation & Submission Finalization | Delete unwanted workspace files, setup root README, and document all 8 hackathon deliverables. | M3 | PLANNED |

## Interface Contracts

### Ask Request API (`POST /ask`)
- **Headers**: `Content-Type: application/json`
- **Body Schema**:
  ```json
  {
    "question": "string",
    "history": [
      {
        "role": "string",
        "content": "string"
      }
    ]
  }
  ```

### Ask Response API (`POST /ask`)
- **Body Schema**:
  ```json
  {
    "answer": "string",
    "sources": [
      {
        "document": "string",
        "chunk": "string"
      }
    ],
    "confidence": "string",
    "routed_to": "string"
  }
  ```

### Ingest Response API (`POST /ingest`)
- **Body Schema**:
  ```json
  {
    "message": "string",
    "chunks": 0
  }
  ```

### Health Response API (`GET /health`)
- **Body Schema**:
  ```json
  {
    "status": "string",
    "version": "string",
    "documents_ingested": true
  }
  ```

## Code Layout
- `app/`
  - `main.py`
  - `config.py`
  - `embeddings.py`
  - `rag.py`
  - `llm.py`
  - `agent.py`
  - `appointment_tool.py`
  - `prompting.py`
  - `schemas.py`
  - `logger.py`
- `data/`
- `vector_store/`
- `tests/`
- `requirements.txt`
- `Dockerfile`
