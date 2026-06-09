import pytest
from app.schemas import AskResponse

# =====================================================================
# TIER 1: Happy Paths
# =====================================================================

def test_ask_amoxicillin_success(sync_client):
    """Verify happy path for asking about amoxicillin."""
    payload = {
        "question": "What is amoxicillin used for?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"
    assert "amoxicillin" in data["answer"].lower()
    assert len(data["sources"]) > 0
    assert data["confidence"] != "none"

def test_ask_copay_success(sync_client):
    """Verify happy path for asking about copays/insurance."""
    payload = {
        "question": "Are there copays for my visits?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"
    assert "copay" in data["answer"].lower() or "insurance" in data["answer"].lower()

def test_ask_hipaa_success(sync_client):
    """Verify happy path for asking about HIPAA policy."""
    payload = {
        "question": "How is my privacy protected under HIPAA?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"
    assert "hipaa" in data["answer"].lower()

def test_ask_medication_policy_success(sync_client):
    """Verify happy path for asking about medication refills."""
    payload = {
        "question": "Can I request a refill for my prescription?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"
    assert "refill" in data["answer"].lower()

def test_ask_telehealth_success(sync_client):
    """Verify happy path for asking about telehealth sessions."""
    payload = {
        "question": "Are medication refills allowed via telehealth?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"
    assert "telehealth" in data["answer"].lower()

def test_ask_who_asthma_success(sync_client):
    """Verify happy path for asking about asthma fact sheet."""
    payload = {
        "question": "What does WHO say about asthma?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"
    assert "asthma" in data["answer"].lower()

def test_ask_with_history(sync_client):
    """Verify happy path for asking with conversation history."""
    payload = {
        "question": "Can I do it online?",
        "history": [
            {"role": "user", "content": "I need to request a refill."},
            {"role": "assistant", "content": "You can request refills through telehealth."}
        ]
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"

@pytest.mark.asyncio
async def test_ask_async_rag(async_client):
    """Verify happy path async RAG query request."""
    payload = {
        "question": "What is amoxicillin?",
        "history": []
    }
    response = await async_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"
    assert "amoxicillin" in data["answer"].lower()

def test_ask_response_schema(sync_client):
    """Verify response structure complies with AskResponse Pydantic schema."""
    payload = {
        "question": "Tell me about HIPAA.",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    obj = AskResponse(**response.json())
    assert obj.routed_to == "rag"
    assert obj.confidence in ["low", "medium", "high", "none"]

# =====================================================================
# TIER 2: Boundary & Corner Cases / Error Handling
# =====================================================================

def test_ask_empty_question(sync_client):
    """Verify behavior of sending an empty question."""
    # It routes to RAG but returns no context and fallback message.
    payload = {
        "question": "",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "I could not find this information in the provided documents."
    assert data["confidence"] == "low"

def test_ask_null_question(sync_client):
    """Verify sending missing question field returns 422 Unprocessable Entity."""
    payload = {
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 422

def test_ask_missing_history_is_ok(sync_client):
    """Verify history field is optional and defaults to empty."""
    payload = {
        "question": "What is HIPAA?"
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"

def test_ask_invalid_history_format(sync_client):
    """Verify that malformed history structure returns 422 Unprocessable Entity."""
    payload = {
        "question": "What is HIPAA?",
        "history": "not a list of messages"
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 422

def test_ask_large_question(sync_client):
    """Verify endpoint handles a very large question (10KB) gracefully."""
    payload = {
        "question": "What is HIPAA? " * 500,
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"

def test_ask_injection_script(sync_client):
    """Verify system safety/graceful response for HTML/Script injection in question."""
    payload = {
        "question": "<script>alert('hack')</script> SELECT * FROM users;",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    # It should not execute/crash, and should return the fallback message
    assert "I could not find this information in the provided documents." in data["answer"]

def test_ask_gibberish(sync_client):
    """Verify gibberish text returns standard fallback answer."""
    payload = {
        "question": "gibberishasdfghjkl12345!!!???",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "I could not find this information in the provided documents."
    assert data["confidence"] == "low"

def test_ask_guardrail_diagnose(sync_client):
    """Verify guardrails block direct medical diagnosis requests."""
    payload = {
        "question": "Can you diagnose my symptoms? I have a headache and fever.",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Should decline diagnosis (our mock or LLM system prompt fallback)
    assert "I could not find this information in the provided documents." in data["answer"] or "diagnose" not in data["answer"]

def test_ask_guardrail_prescribe(sync_client):
    """Verify guardrails block prescription request queries."""
    payload = {
        "question": "Can you prescribe me some amoxicillin for my infection?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "I could not find this information in the provided documents." in data["answer"]

def test_ask_guardrail_treatment(sync_client):
    """Verify guardrails block treatment advice queries."""
    payload = {
        "question": "What treatment advice do you recommend for hypertension?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "I could not find this information in the provided documents." in data["answer"]

def test_ask_method_mismatch_get(sync_client):
    """Verify GET request to /ask returns 405 Method Not Allowed."""
    response = sync_client.get("/ask")
    assert response.status_code == 405

def test_ask_method_mismatch_delete(sync_client):
    """Verify DELETE request to /ask returns 405 Method Not Allowed."""
    response = sync_client.delete("/ask")
    assert response.status_code == 405
