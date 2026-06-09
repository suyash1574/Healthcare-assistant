import pytest

# =====================================================================
# TIER 4: Real-World Multi-Turn Patient Journeys / Scenarios
# =====================================================================

def test_scenario_new_patient_journey(sync_client):
    """Scenario 1: Onboarding a new patient.
    Steps:
      1. Ask about HIPAA privacy policy.
      2. Ask about insurance copays.
      3. Ask about required documents before arrival.
      4. Book an appointment with a dermatologist on Thursday.
    """
    history = []

    # Step 1: HIPAA privacy check
    q1 = "How is my privacy protected?"
    res1 = sync_client.post("/ask", json={"question": q1, "history": history})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["routed_to"] == "rag"
    assert "hipaa" in data1["answer"].lower()
    history.append({"role": "user", "content": q1})
    history.append({"role": "assistant", "content": data1["answer"]})

    # Step 2: Copay/insurance check
    q2 = "Are there any copays for my visit?"
    res2 = sync_client.post("/ask", json={"question": q2, "history": history})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["routed_to"] == "rag"
    assert "copay" in data2["answer"].lower() or "insurance" in data2["answer"].lower()
    history.append({"role": "user", "content": q2})
    history.append({"role": "assistant", "content": data2["answer"]})

    # Step 3: Preparation details (knowledge keywords)
    q3 = "What do I need to bring to my appointment?"
    res3 = sync_client.post("/ask", json={"question": q3, "history": history})
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["routed_to"] == "rag"
    assert "appointment policy" in data3["answer"].lower() or "documents" in data3["answer"].lower() or "bring" in data3["answer"].lower()
    history.append({"role": "user", "content": q3})
    history.append({"role": "assistant", "content": data3["answer"]})

    # Step 4: Book dermatologist
    q4 = "Okay, I want to book a dermatologist on Thursday."
    res4 = sync_client.post("/ask", json={"question": q4, "history": history})
    assert res4.status_code == 200
    data4 = res4.json()
    assert data4["routed_to"] == "appointment"
    assert "Dermatology" in data4["answer"]
    assert "Thursday 3:00 PM" in data4["answer"]


def test_scenario_chronic_disease_refill(sync_client):
    """Scenario 2: Chronic asthma patient requesting refill and scheduling.
    Steps:
      1. Ask about WHO recommendations for asthma.
      2. Ask about medication refill policy.
      3. Ask about requesting refill via telehealth.
      4. Schedule a pediatric slot on Tuesday.
    """
    history = []

    # Step 1: Asthma info
    q1 = "What does WHO say about asthma?"
    res1 = sync_client.post("/ask", json={"question": q1, "history": history})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["routed_to"] == "rag"
    assert "asthma" in data1["answer"].lower()
    history.append({"role": "user", "content": q1})
    history.append({"role": "assistant", "content": data1["answer"]})

    # Step 2: Refill policy
    q2 = "How do I request a refill?"
    res2 = sync_client.post("/ask", json={"question": q2, "history": history})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["routed_to"] == "rag"
    assert "refill" in data2["answer"].lower()
    history.append({"role": "user", "content": q2})
    history.append({"role": "assistant", "content": data2["answer"]})

    # Step 3: Telehealth availability
    q3 = "Can I do a telehealth session for the refill?"
    res3 = sync_client.post("/ask", json={"question": q3, "history": history})
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["routed_to"] == "rag"
    assert "telehealth" in data3["answer"].lower()
    history.append({"role": "user", "content": q3})
    history.append({"role": "assistant", "content": data3["answer"]})

    # Step 4: Schedule pediatric appointment
    q4 = "Please schedule a slot with pediatric clinic on Tuesday."
    res4 = sync_client.post("/ask", json={"question": q4, "history": history})
    assert res4.status_code == 200
    data4 = res4.json()
    assert data4["routed_to"] == "appointment"
    assert "Pediatrics" in data4["answer"]
    assert "Tuesday 9:00 AM" in data4["answer"]


def test_scenario_emergency_deflection_chest_pain(sync_client):
    """Scenario 3: Emergency chest pain query deflection.
    Verify that emergency symptoms trigger an immediate call 911 / emergency room recommendation.
    """
    payload = {
        "question": "I am having severe chest pain and difficulty breathing. Can you help?",
        "history": []
    }
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    # It must refuse diagnostic/treatment advice and direct to emergency (911)
    answer = data["answer"].lower()
    assert "911" in answer or "emergency room" in answer or "immediate" in answer


def test_scenario_appointment_cancellation_flow(sync_client):
    """Scenario 4: Patient checking cancellation policy and canceling.
    Steps:
      1. Ask about cancellation policies.
      2. Call the cancel appointment action.
    """
    history = []

    # Step 1: Cancellation policy check
    q1 = "What is the cancellation policy for appointments?"
    res1 = sync_client.post("/ask", json={"question": q1, "history": history})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["routed_to"] == "rag"
    assert "cancel" in data1["answer"].lower() or "24 hours" in data1["answer"].lower()
    history.append({"role": "user", "content": q1})
    history.append({"role": "assistant", "content": data1["answer"]})

    # Step 2: Cancel appointment action
    q2 = "I need to cancel my appointment today."
    res2 = sync_client.post("/ask", json={"question": q2, "history": history})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["routed_to"] == "appointment"
    assert "General" in data2["answer"]
