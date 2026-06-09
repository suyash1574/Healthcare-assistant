# Implementation Plan

[Overview]
Build a FastAPI-based Healthcare AI Assistant that ingests healthcare documents into ChromaDB using sentence-transformer embeddings, answers user questions with RAG from retrieved chunks using a Groq-hosted LLM, provides source citations, routes appointment-related queries to a dedicated tool, and serves a simple HTML/CSS/JS UI—packaged and runnable via Docker.

Multiple paragraphs outlining the scope, context, and high-level approach. Explain why this implementation is needed and how it fits into the existing system.

This implementation is required because the assignment mandates: document ingestion, vector embeddings, ChromaDB storage, retrieval-augmented question answering with citations, explicit hallucination prevention (refusal when relevant information isn’t found), appointment routing to a tool, API exposure, a basic web UI, and Docker support. Since the target directory is empty, the solution will be implemented as a fresh project scaffold under `healthcare-ai-assistant/` with a clear separation between configuration, ingestion, retrieval (RAG), LLM prompting, routing/tool behavior, logging, and HTTP endpoints.

The system will:
1) ingest the provided `data/*.txt` documents by chunking, embedding with `sentence-transformers` (`all-MiniLM-L6-v2`), and storing vectors in a local ChromaDB persistent directory;
2) answer questions by embedding the question, retrieving top-k chunks from ChromaDB, and then invoking a Groq LLM with a strict “answer only from context” prompt;
3) attach citations by returning the originating document names for retrieved chunks;
4) avoid hallucinations by refusing when no relevant chunks are retrieved or when similarity is below a configured threshold;
5) detect appointment intents and route them to an appointment tool (mocked slot availability and booking flow) instead of running RAG;
6) expose `/health`, `POST /ingest`, and `POST /ask` APIs;
7) provide a minimal frontend that calls `/ask` and renders answer + sources.

[Types]
Define request/response data structures and internal routing/tool parameters for consistent validation and response formatting.

Detailed type definitions, interfaces, enums, or data structures with complete specifications. Include field names, types, validation rules, and relationships.

- `IngestResponse`
  - `message: str` (always “Documents ingested successfully” on success)
- `AskRequest`
  - `question: str` (min length 1, max length 5000)
- `SourceCitation`
  - `document: str` (document filename, e.g., `telehealth.txt`)
  - `chunk_id: str` (stable id derived from source + chunk index)
- `AskResponse`
  - `answer: str`
  - `sources: list[SourceCitation]` (empty list when refusal happens)
  - `routed_to: str` (enum-like: `"rag"` or `"appointment"`)
- Internal:
  - `RetrievedChunk`
    - `text: str`
    - `document: str`
    - `chunk_id: str`
    - `score: float` (similarity/distance score from Chroma)
  - `AppointmentSlots`
    - `slots: list[str]` (mocked availability)
  - `AppointmentBooking`
    - `slot: str`
    - `confirmation_id: str`
    - `status: str` (e.g., `"confirmed"`)
- Routing intent:
  - `AppointmentIntent`: boolean derived from keyword heuristics + optional regex patterns:
    - matches words/phrases like: `book`, `schedule`, `appointment`, `reschedule`, `cancel`, `cardiology`, `dermatology`, `primary care`, etc.

Validation rules:
- Reject empty question with HTTP 422 (FastAPI/Pydantic validation).
- Enforce refusal if retrieval does not pass thresholds.

[Files]
Single sentence describing file modifications.

Detailed breakdown:
- New files to be created (with full paths and purpose)
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/README.md` — setup and architecture documentation
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/requirements.txt` — Python dependencies
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/Dockerfile` — container build and uvicorn run
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/.env.example` — example env vars
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/main.py` — FastAPI app, routes `/health`, `/ingest`, `/ask`
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/config.py` — config loading (env, thresholds, model names, paths)
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/logger.py` — structured logging setup
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/data_loader.py` — load all `data/*.txt` files
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/embeddings.py` — embedding model initialization and encoding helpers
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/vector_store.py` — ChromaDB persistent client and collection management
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/ingest.py` — chunking + embedding + vector upsert
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/retrieval.py` — question embedding + top-k retrieval + thresholding
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/llm.py` — Groq LLM client and prompt construction
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/router.py` — intent detection and routing to RAG vs appointment tool
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/appointment_tool.py` — appointment slot listing + booking (mock)
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/prompting.py` — strict system prompt template and refusal rules
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/app/schemas.py` — Pydantic models for API I/O
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/frontend/index.html` — UI markup
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/frontend/style.css` — basic styling
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/frontend/script.js` — calls `/ask` and renders chat
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/data/telehealth.txt`
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/data/appointment_policy.txt`
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/data/insurance_faq.txt`
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/data/medication_policy.txt`
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/data/hipaa_policy.txt`
  - `d:/Projects/MINDBowser ASSIGNMENT/healthcare-ai-assistant/vector_store/.gitkeep` — ensures persistent dir exists (Chroma will create files)
- Configuration file updates
  - None beyond `.env.example` and local config in `app/config.py`.

[Functions]
Single sentence describing function modifications.

Detailed breakdown:
- New functions
  - `load_healthcare_documents(data_dir: str) -> list[Document]` in `app/data_loader.py`
  - `chunk_documents(docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Chunk]` in `app/ingest.py` (or `app/ingest.py`)
  - `get_embedding_model(model_name: str)` and `embed_texts(texts: list[str]) -> list[list[float]]` in `app/embeddings.py`
  - `get_chroma_collection(collection_name: str, persist_dir: str)` in `app/vector_store.py`
  - `ingest_documents()` in `app/ingest.py` — loads docs, chunks, embeds, upserts to Chroma with metadata:
    - `document` (filename)
    - `chunk_id`
  - `retrieve(question: str, top_k: int, score_threshold: float) -> tuple[list[RetrievedChunk], float]` in `app/retrieval.py`
  - `build_rag_prompt(context: str, question: str) -> str` in `app/prompting.py`
  - `generate_answer(prompt: str) -> str` in `app/llm.py`
  - `route_question(question: str) -> Literal["rag","appointment"]` in `app/router.py`
  - `check_available_slots() -> list[str]` in `app/appointment_tool.py`
  - `book_appointment(slot: str) -> AppointmentBooking` in `app/appointment_tool.py`
- Modified functions
  - None (fresh project).
- Removed functions
  - None.

[Classes]
Single sentence describing class modifications.

Detailed breakdown:
- New classes
  - None required; primarily use Pydantic models and functional modules.
- Modified classes
  - None.
- Removed classes
  - None.

[Dependencies]
Single sentence describing dependency modifications.

Details of new packages, version changes, and integration requirements.

Dependencies (install via `pip`):
- `fastapi`
- `uvicorn`
- `python-dotenv`
- `pypdf` (optional if later supporting PDF; for current assignment only txt is used but can be included)
- `chromadb`
- `langchain`
- `langchain-community`
- `langchain-text-splitters`
- `sentence-transformers`
- `groq`
Optional/utility dependencies:
- `tiktoken` not required (sentence-transformers)
- `jinja2` not required (simple JS frontend)

ChromaDB:
- Use persistent local directory: `vector_store/`.

LLM:
- Use Groq API with `groq` SDK and environment variable `GROQ_API_KEY`.

Embeddings:
- Use sentence-transformers model `all-MiniLM-L6-v2`.

[Testing]
Single sentence describing testing approach.

Test file requirements, existing test modifications, and validation strategies.

- Add lightweight smoke tests in `app/tests/test_smoke.py` (optional depending on repo constraints) or run manual curl-based checks:
  1) `POST /ingest` returns success.
  2) `POST /ask` with known question returns answer + at least one source citation.
  3) `POST /ask` with an out-of-scope question returns refusal string and empty sources.
  4) Appointment question routes to `"appointment"` and returns mocked slots/confirmation.
- Validate:
  - retrieval threshold triggers refusal,
  - citations correspond to metadata of retrieved chunks.

[Implementation Order]
Single sentence describing the implementation sequence.

Numbered steps showing the logical order of changes to minimize conflicts and ensure successful integration.

1) Create project scaffold: `healthcare-ai-assistant/` structure, `requirements.txt`, `.env.example`, and `Dockerfile`.
2) Add `data/*.txt` documents and implement loader/chunking/ingestion pipeline writing to persistent ChromaDB.
3) Implement retrieval + hallucination prevention thresholding logic and return retrieved chunk metadata for citations.
4) Implement Groq LLM prompting with strict rules and integrate RAG answer generation.
5) Implement appointment router + appointment tool and integrate into `/ask` route.
6) Add FastAPI endpoints: `/health`, `POST /ingest`, `POST /ask` returning `AskResponse` with `sources` and `routed_to`.
7) Add logging across ingestion, retrieval, routing, and LLM response generation.
8) Build frontend (`index.html`, `style.css`, `script.js`) and wire it to the backend `/ask` endpoint.
9) Validate end-to-end locally, then ensure Docker build/run works and README documents setup + architecture.
