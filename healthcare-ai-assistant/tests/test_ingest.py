import pytest
from app.schemas import IngestResponse

# =====================================================================
# TIER 1: Happy Paths
# =====================================================================

def test_ingest_success_sync(sync_client):
    """Verify that manual ingestion triggers successfully and returns the chunk count (sync)."""
    response = sync_client.post("/ingest")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "chunks" in data
    assert data["chunks"] > 0
    assert data["message"] == "Ingestion complete"

@pytest.mark.asyncio
async def test_ingest_success_async(async_client):
    """Verify that manual ingestion triggers successfully and returns the chunk count (async)."""
    response = await async_client.post("/ingest")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "chunks" in data
    assert data["chunks"] > 0
    assert data["message"] == "Ingestion complete"

def test_ingest_response_schema(sync_client):
    """Verify response payload matches the IngestResponse schema."""
    response = sync_client.post("/ingest")
    assert response.status_code == 200
    obj = IngestResponse(**response.json())
    assert obj.message == "Ingestion complete"
    assert obj.chunks > 0

# =====================================================================
# TIER 2: Boundary & Corner Cases / Error Handling
# =====================================================================

def test_ingest_method_mismatch_get(sync_client):
    """Verify GET request to /ingest returns 405 Method Not Allowed."""
    response = sync_client.get("/ingest")
    assert response.status_code == 405

def test_ingest_method_mismatch_put(sync_client):
    """Verify PUT request to /ingest returns 405 Method Not Allowed."""
    response = sync_client.put("/ingest")
    assert response.status_code == 405

def test_ingest_method_mismatch_delete(sync_client):
    """Verify DELETE request to /ingest returns 405 Method Not Allowed."""
    response = sync_client.delete("/ingest")
    assert response.status_code == 405

def test_ingest_with_ignored_payload(sync_client):
    """Verify POST request to /ingest with payload is accepted and payload is ignored (FastAPI behavior)."""
    payload = {"some_extra_field": "should_be_ignored", "value": 123}
    response = sync_client.post("/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Ingestion complete"

def test_ingest_with_large_payload_ignored(sync_client):
    """Verify POST request to /ingest with a very large payload is accepted and ignored."""
    payload = {"huge_field": "x" * 10000}
    response = sync_client.post("/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Ingestion complete"

def test_ingest_multiple_times(sync_client):
    """Verify that calling /ingest multiple times consecutively succeeds and returns chunks count consistently."""
    response1 = sync_client.post("/ingest")
    assert response1.status_code == 200
    chunks1 = response1.json()["chunks"]
    
    response2 = sync_client.post("/ingest")
    assert response2.status_code == 200
    chunks2 = response2.json()["chunks"]
    
    assert chunks1 == chunks2
