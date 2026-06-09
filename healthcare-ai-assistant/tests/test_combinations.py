import pytest
from app.appointment_tool import book_appointment, get_bookings, BOOKINGS

# =====================================================================
# TIER 3: Cross-Feature Sequential & Combination Tests
# =====================================================================

def test_ingest_then_query_sequence(sync_client):
    """Verify sequence of Ingest -> Ask RAG -> Ingest -> Ask RAG."""
    # 1. First Ingestion
    res_ingest1 = sync_client.post("/ingest")
    assert res_ingest1.status_code == 200
    
    # 2. RAG Query
    res_ask1 = sync_client.post("/ask", json={"question": "What is amoxicillin?"})
    assert res_ask1.status_code == 200
    assert "amoxicillin" in res_ask1.json()["answer"].lower()
    
    # 3. Second Ingestion (Re-ingestion)
    res_ingest2 = sync_client.post("/ingest")
    assert res_ingest2.status_code == 200
    
    # 4. RAG Query again
    res_ask2 = sync_client.post("/ask", json={"question": "What is amoxicillin?"})
    assert res_ask2.status_code == 200
    assert "amoxicillin" in res_ask2.json()["answer"].lower()


def test_switch_intent_booking_to_rag_in_history(sync_client):
    """Verify agentic routing correctly identifies intent when history is present."""
    # Turn 1: Booking inquiry (routes to appointment)
    res1 = sync_client.post("/ask", json={
        "question": "I want to see a cardiologist on Monday",
        "history": []
    })
    assert res1.status_code == 200
    assert res1.json()["routed_to"] == "appointment"
    
    # Turn 2: Switching to RAG informational question about copay with history
    res2 = sync_client.post("/ask", json={
        "question": "Are there any copays for my visit?",
        "history": [
            {"role": "user", "content": "I want to see a cardiologist on Monday"},
            {"role": "assistant", "content": res1.json()["answer"]}
        ]
    })
    assert res2.status_code == 200
    assert res2.json()["routed_to"] == "rag"
    assert "copay" in res2.json()["answer"].lower() or "insurance" in res2.json()["answer"].lower()


def test_switch_intent_rag_to_booking_in_history(sync_client):
    """Verify that asking a RAG question then booking works sequentially with history."""
    # Turn 1: RAG query about telehealth
    res1 = sync_client.post("/ask", json={
        "question": "Can a patient request a medication refill through telehealth?",
        "history": []
    })
    assert res1.status_code == 200
    assert res1.json()["routed_to"] == "rag"
    
    # Turn 2: Switching to scheduling booking request
    res2 = sync_client.post("/ask", json={
        "question": "Great, then I want to schedule a visit with dermatology",
        "history": [
            {"role": "user", "content": "Can a patient request a medication refill through telehealth?"},
            {"role": "assistant", "content": res1.json()["answer"]}
        ]
    })
    assert res2.status_code == 200
    assert res2.json()["routed_to"] == "appointment"
    assert "Dermatology" in res2.json()["answer"]


def test_booking_lifecycle_state():
    """Verify mock booking lifecycle directly in-memory state."""
    # 1. Check bookings empty
    assert len(get_bookings()) == 0
    
    # 2. Book an appointment
    res = book_appointment(
        department="cardiology",
        date="Monday",
        slot="Monday 10:00 AM",
        patient_name="John Doe"
    )
    assert res["status"] == "confirmed"
    assert "successfully" in res["message"]
    
    # 3. Check booking is stored
    bookings = get_bookings()
    assert len(bookings) == 1
    assert bookings[0]["patient_name"] == "John Doe"
    assert bookings[0]["department"] == "Cardiology"
    assert bookings[0]["slot"] == "Monday 10:00 AM"


def test_double_booking_prevention():
    """Verify slot cannot be double booked for same department/date."""
    # 1. Book first time
    res1 = book_appointment(
        department="cardiology",
        date="Monday",
        slot="Monday 10:00 AM",
        patient_name="Alice"
    )
    assert res1["status"] == "confirmed"
    
    # 2. Try to book the same slot again
    res2 = book_appointment(
        department="cardiology",
        date="Monday",
        slot="Monday 10:00 AM",
        patient_name="Bob"
    )
    assert res2["status"] == "failed"
    assert "already booked" in res2["message"]
    
    # Verify only 1 booking was created
    assert len(get_bookings()) == 1


def test_book_invalid_slot():
    """Verify booking fails if slot is not in department available list."""
    res = book_appointment(
        department="cardiology",
        date="Monday",
        slot="Sunday 5:00 PM", # invalid slot
        patient_name="Charlie"
    )
    assert res["status"] == "failed"
    assert "not available" in res["message"]
    assert len(get_bookings()) == 0


def test_get_bookings_filtering():
    """Verify that retrieval filtering by patient name works."""
    book_appointment("cardiology", "Monday", "Monday 10:00 AM", "John")
    book_appointment("dermatology", "Tuesday", "Tuesday 11:00 AM", "Sarah")
    
    all_bookings = get_bookings()
    assert len(all_bookings) == 2
    
    john_bookings = get_bookings("John")
    assert len(john_bookings) == 1
    assert john_bookings[0]["patient_name"] == "John"
    
    sarah_bookings = get_bookings("sarah")
    assert len(sarah_bookings) == 1
    assert sarah_bookings[0]["patient_name"].lower() == "sarah"

