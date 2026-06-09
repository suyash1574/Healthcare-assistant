# Healthcare AI Assistant - Test Infrastructure Documentation

This document explains the test suite architecture, environment configuration, setup requirements, and commands to run tests.

## Test Suite Architecture

The Healthcare AI Assistant test suite is a comprehensive, end-to-end (E2E) testing framework designed to validate both the API layer and the underlying agentic routing, RAG retrieval, and policy guardrails.

The tests are organized into **4 Tiers** located in the `tests/` directory:

1. **Tier 1: Feature Coverage (Happy Paths)**
   - Verification of the core system features: health checks, document ingestion, informational RAG queries, scheduling slot lookups, and general API responses.
2. **Tier 2: Boundary & Corner Cases**
   - Boundary tests including empty or null payloads, missing query fields, method mismatches (e.g. GET/PUT on POST endpoints), large payloads, SQL/Script injections, and gibberish input fallback validation.
3. **Tier 3: Cross-Feature Combinations**
   - Sequential workflows such as ingestion followed by querying, re-ingestion, and conversational state tracking with intent switching inside chat history (e.g., booking -> RAG -> booking).
4. **Tier 4: Real-World Patient Journeys**
   - Complete multi-turn scenarios mimicking patient behavior: onboarding, chronic illness medication refill workflow, emergency deflection, and appointment cancellation.

## Key Test Infrastructure Components

- **`tests/conftest.py`**:
  - **Unified Client Fixture**: Provides synchronous (`sync_client`) and asynchronous (`async_client`) clients. It reads the `BASE_URL` environment variable. If `BASE_URL` is set to a live URL, tests run as a pure HTTP client targeting that address. If it is `"local"` or empty, it runs FastAPI's `TestClient` in-process.
  - **Mock LLMs & Embeddings**: Overrides `ChatGroq`, `ChatOpenAI`, and `HuggingFaceEmbeddings` when running locally to eliminate network latency, API costs, and dependency on external servers.
  - **Retrieval Mocking**: Monkeypatches the internal `retrieve_context` function in local mode to return mock document passages matching specific keywords, ensuring tests are deterministic.
  - **Vector Store Isolation**: Automatically uses a temporary directory for `VECTOR_STORE_DIR` during test runs, preventing tests from corrupting developer data.
  - **State Isolation**: Automatically clears in-memory booking records between each test.

- **`tests/pytest.ini`**: Pytest configuration setting pathing, asyncio auto-mode, and default verbose command line arguments.
- **`tests/requirements-test.txt`**: Declares test dependencies (`pytest`, `httpx`, `pytest-cov`, `pytest-asyncio`).

## Setup and Execution

### Prerequisites
Make sure the main project dependencies are installed in your virtual environment:
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Install Testing Dependencies
Install the testing packages:
```powershell
.\venv\Scripts\python.exe -m pip install -r tests/requirements-test.txt
```

### Run Tests Locally (with Mocks)
To execute all tests locally using mocks:
```powershell
.\venv\Scripts\python.exe -m pytest
```

To run with coverage reporting:
```powershell
.\venv\Scripts\python.exe -m pytest --cov=app tests/
```

### Run Tests Against Live Server (Opaque-Box E2E Mode)
To run the test suite against a running instance of the app (e.g., `http://localhost:8000`):
```powershell
$env:BASE_URL="http://localhost:8000"
.\venv\Scripts\python.exe -m pytest
```
*Note: In live mode, mocks are disabled, and real requests are processed by the target server.*
