import pytest

# =====================================================================
# TIER 1: Happy Paths
# =====================================================================

def test_route_booking_cardiology_success(sync_client):
    """Verify that asking to book cardiology routes to appointment tool with correct department."""
    payload = {"question": "I want to book an appointment with a cardiologist"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Cardiology" in data["answer"]
    assert "Monday 10:00 AM" in data["answer"]

def test_route_booking_dermatology_success(sync_client):
    """Verify that scheduling dermatology routes to appointment tool."""
    payload = {"question": "Can I schedule a visit for dermatology?"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Dermatology" in data["answer"]

def test_route_booking_neurology_success(sync_client):
    """Verify that scheduling neurology routes to appointment tool."""
    payload = {"question": "I need to set up an appointment with a neurologist"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Neurology" in data["answer"]

def test_route_booking_pediatrics_success(sync_client):
    """Verify that booking pediatrics routes to appointment tool."""
    payload = {"question": "book a slot with a pediatrician"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Pediatrics" in data["answer"]

def test_route_booking_general_success(sync_client):
    """Verify that generic appointment request routes to general department."""
    payload = {"question": "book a visit"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "General" in data["answer"]

def test_route_availability_orthopedics_success(sync_client):
    """Verify availability request routes to appointment tool."""
    payload = {"question": "show me available slots for orthopedics"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Orthopedics" in data["answer"]

def test_route_action_cancel_success(sync_client):
    """Verify cancel intent routes to appointment tool."""
    payload = {"question": "cancel my appointment"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "General" in data["answer"]

def test_route_action_reschedule_success(sync_client):
    """Verify reschedule intent routes to appointment tool."""
    payload = {"question": "reschedule my appointment"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "General" in data["answer"]

# =====================================================================
# TIER 2: Boundary & Corner Cases / Alias Resolution
# =====================================================================

def test_alias_heart_doctor_to_cardiology(sync_client):
    """Verify 'heart' alias routes to Cardiology."""
    payload = {"question": "I want to see a heart doctor"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Cardiology" in data["answer"]

def test_alias_skin_specialist_to_dermatology(sync_client):
    """Verify 'skin' alias routes to Dermatology."""
    payload = {"question": "schedule with a skin specialist"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Dermatology" in data["answer"]

def test_alias_brain_specialist_to_neurology(sync_client):
    """Verify 'brain' alias routes to Neurology."""
    payload = {"question": "book a visit for brain issues"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Neurology" in data["answer"]

def test_alias_kids_to_pediatrics(sync_client):
    """Verify 'kids' alias routes to Pediatrics."""
    payload = {"question": "schedule an appointment for my kids"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Pediatrics" in data["answer"]

def test_alias_bone_to_orthopedics(sync_client):
    """Verify 'bone' alias routes to Orthopedics."""
    payload = {"question": "I need to see a bone specialist"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Orthopedics" in data["answer"]

def test_date_monday_filter(sync_client):
    """Verify day-of-week slots filtering (Monday)."""
    payload = {"question": "available slots for cardiology on Monday"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Monday 10:00 AM" in data["answer"]
    assert "Wednesday" not in data["answer"]

def test_date_tuesday_filter(sync_client):
    """Verify day-of-week slots filtering (Tuesday)."""
    payload = {"question": "can I schedule with dermatology on Tuesday"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Tuesday 11:00 AM" in data["answer"]
    assert "Thursday" not in data["answer"]

def test_date_no_slots_on_day(sync_client):
    """Verify slot response when department has no slots on requested day."""
    # Pediatrics has Tuesday, Wednesday, Friday slots. Monday should return "No slots available" msg.
    payload = {"question": "available slots for pediatrics on Monday"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "No slots available on Monday" in data["answer"]

def test_knowledge_keywords_override_booking(sync_client):
    """Verify knowledge questions about appointments route to RAG, not booking."""
    payload = {"question": "what documents do I need to bring to my appointment?"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "rag"

def test_route_empty_department_fallback(sync_client):
    """Verify fallback to general department if booking intent doesn't specify department."""
    payload = {"question": "I would like to reserve a slot"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "General" in data["answer"]

def test_alias_women_to_gynecology(sync_client):
    """Verify 'women' alias routes to Gynecology."""
    payload = {"question": "book slot for women department"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Gynecology" in data["answer"]

def test_alias_kidney_to_urology(sync_client):
    """Verify 'kidney' alias routes to Urology."""
    payload = {"question": "schedule visit for kidney issue"}
    response = sync_client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "appointment"
    assert "Urology" in data["answer"]
