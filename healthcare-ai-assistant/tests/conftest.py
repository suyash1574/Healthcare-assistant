import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock

# Read BASE_URL from environment
BASE_URL = os.environ.get("BASE_URL", "local")
IS_LOCAL = (BASE_URL == "local" or not BASE_URL)

# Mocking LLMs and Embeddings BEFORE importing application modules
if IS_LOCAL:
    # Mock HuggingFaceEmbeddings
    class MockHuggingFaceEmbeddings:
        def __init__(self, *args, **kwargs):
            pass

        def embed_documents(self, texts):
            import hashlib
            embeddings = []
            for text in texts:
                h = hashlib.sha256(text.encode('utf-8')).digest()
                vector = [float(b)/255.0 for b in h]
                vector = (vector * 12)[:384]
                embeddings.append(vector)
            return embeddings

        def embed_query(self, text):
            import hashlib
            h = hashlib.sha256(text.encode('utf-8')).digest()
            vector = [float(b)/255.0 for b in h]
            return (vector * 12)[:384]

    import langchain_huggingface
    langchain_huggingface.HuggingFaceEmbeddings = MockHuggingFaceEmbeddings

    # Inject dummy API keys for local runs to prevent skipping providers
    import app.config
    app.config.GROQ_API_KEY = "mock_key"
    app.config.NVIDIA_API_KEY = "mock_key"
    app.config.OPENROUTER_API_KEY = "mock_key"
    for provider in app.config.LLM_PROVIDERS:
        provider["api_key"] = "mock_key"

    # Mock ChatGroq and ChatOpenAI using LangChain's Runnable interface
    from langchain_core.runnables import Runnable
    from langchain_core.messages import AIMessage
    
    class MockLLM(Runnable):
        def __init__(self, *args, **kwargs):
            super().__init__()

        def invoke(self, input_data, config=None, **kwargs):
            text = str(input_data)
            
            # Extract question part to avoid matching system prompt keywords (e.g. "treatment advice")
            question_part = text
            if "Question:" in text:
                question_part = text.split("Question:")[-1]
            elif "content=" in text:
                parts = text.split("HumanMessage(content=")
                if len(parts) > 1:
                    question_part = parts[-1]
            
            q = question_part.lower()
            
            # Emergency deflection
            if any(w in q for w in ["chest pain", "shortness of breath", "difficulty breathing", "breathing"]):
                content = "I cannot provide medical advice. If you are experiencing a medical emergency (like severe chest pain or breathing difficulty), please call 911 or go to the nearest emergency room immediately."
            # Diagnostic and treatment advice guardrails (removed prescription to avoid blocking general refill requests)
            elif any(w in q for w in ["diagnose", "prescribe", "treatment advice"]):
                content = "I could not find this information in the provided documents."
            elif "amoxicillin" in q:
                content = "Amoxicillin is an antibiotic used to treat bacterial infections. According to fda_drug_amoxicillin.txt, it should be taken as prescribed."
            elif "telehealth" in q:
                content = "According to telehealth.txt, patients can request a medication refill through telehealth sessions."
            elif "refill" in q:
                content = "Under the medication refill policy, patients can request refills for active prescriptions if they have refills remaining."
            elif "copay" in q or "insurance" in q:
                content = "According to insurance_faq.txt, copays are due at the time of service."
            elif "asthma" in q:
                content = "According to who_asthma_fact_sheet.txt, asthma is a chronic disease affecting the airways."
            elif "hipaa" in q or "privacy" in q:
                content = "According to hipaa_policy.txt, patient health information is protected under HIPAA."
            elif "appointment policy" in q or "cancel" in q or "reschedule" in q:
                content = "According to appointment_policy.txt, appointments must be cancelled at least 24 hours in advance."
            else:
                content = "According to the provided documents, we have the relevant health information."
            
            return AIMessage(content=content)

    import langchain_groq
    import langchain_openai
    langchain_groq.ChatGroq = MockLLM
    langchain_openai.ChatOpenAI = MockLLM

    # Mock retrieve_context in app.rag to avoid vector database querying in local mode
    def mock_retrieve_context(question: str):
        q = question.lower()
        if not q.strip():
            return [], []
        if any(w in q for w in ["chest pain", "shortness of breath", "difficulty breathing", "breathing"]):
            return ["Emergency guidelines: Call 911."], [{"document": "emergency_guidelines.txt", "chunk": "Emergency call 911"}]
        if "amoxicillin" in q:
            return ["Amoxicillin is an antibiotic..."], [{"document": "fda_drug_amoxicillin.txt", "chunk": "Amoxicillin..."}]
        elif "refill" in q:
            return ["Medication refill policy..."], [{"document": "medication_policy.txt", "chunk": "Medication refill..."}]
        elif "telehealth" in q:
            return ["Telehealth policy..."], [{"document": "telehealth.txt", "chunk": "Telehealth..."}]
        elif "copay" in q or "insurance" in q:
            return ["Insurance FAQ copay..."], [{"document": "insurance_faq.txt", "chunk": "Insurance FAQ..."}]
        elif "asthma" in q:
            return ["Asthma is a chronic disease..."], [{"document": "who_asthma_fact_sheet.txt", "chunk": "Asthma..."}]
        elif "hipaa" in q or "privacy" in q:
            return ["HIPAA policy..."], [{"document": "hipaa_policy.txt", "chunk": "HIPAA..."}]
        elif "appointment policy" in q or "cancel" in q or "reschedule" in q:
            return ["Appointment cancel policy..."], [{"document": "appointment_policy.txt", "chunk": "Appointment policy..."}]
        elif any(w in q for w in ["diagnose", "prescribe", "treatment advice"]):
            return ["Medical context..."], [{"document": "medical_doc.txt", "chunk": "Medical..."}]
        elif "gibberish" in q or "asdf" in q or "!!!" in q:
            return [], []
        else:
            return ["General health context..."], [{"document": "general.txt", "chunk": "General..."}]

    import app.rag
    app.rag.retrieve_context = mock_retrieve_context


# Setup temporary vector store for isolation
@pytest.fixture(scope="session", autouse=True)
def temp_vector_store():
    if IS_LOCAL:
        import app.config
        temp_dir = tempfile.mkdtemp(prefix="test_vector_store_")
        orig_dir = app.config.VECTOR_STORE_DIR
        app.config.VECTOR_STORE_DIR = temp_dir
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
        app.config.VECTOR_STORE_DIR = orig_dir
    else:
        yield None

# Clean bookings before each test case
@pytest.fixture(autouse=True)
def clean_bookings():
    if IS_LOCAL:
        from app.appointment_tool import BOOKINGS
        BOOKINGS.clear()

# Sync Client Fixture (Function scoped)
@pytest.fixture(scope="function")
def sync_client():
    if IS_LOCAL:
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as c:
            yield c
    else:
        import httpx
        with httpx.Client(base_url=BASE_URL) as c:
            yield c

# Async Client Fixture (Function scoped)
@pytest.fixture(scope="function")
async def async_client():
    if IS_LOCAL:
        import httpx
        from app.main import app
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
            yield c
    else:
        import httpx
        async with httpx.AsyncClient(base_url=BASE_URL) as c:
            yield c

