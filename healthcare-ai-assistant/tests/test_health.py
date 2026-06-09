import pytest
from app.schemas import HealthResponse

# =====================================================================
# TIER 1: Happy Paths
# =====================================================================

def test_health_check_sync(sync_client):
    """Verify that the health check endpoint returns 200 OK and healthy status (sync)."""
    response = sync_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"
    assert data["documents_ingested"] is True

@pytest.mark.asyncio
async def test_health_check_async(async_client):
    """Verify that the health check endpoint returns 200 OK and healthy status (async)."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"
    assert data["documents_ingested"] is True

def test_health_check_response_schema(sync_client):
    """Validate health check response schema using Pydantic model."""
    response = sync_client.get("/health")
    assert response.status_code == 200
    # This will raise an error if response doesn't match HealthResponse schema
    obj = HealthResponse(**response.json())
    assert obj.status == "healthy"

def test_root_index_html(sync_client):
    """Verify that root endpoint GET / returns index.html content (static mount)."""
    response = sync_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Healthcare AI Assistant" in response.text or "<div" in response.text

def test_static_index_html(sync_client):
    """Verify static mount accesses index.html under /static/index.html (if mounted)."""
    # Note: main.py mounts frontend_dir to /static, so /static/index.html should serve it.
    response = sync_client.get("/static/index.html")
    # If the index.html is in frontend/, it should be found.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

# =====================================================================
# TIER 2: Boundary & Corner Cases / Error Handling
# =====================================================================

def test_health_check_method_mismatch_post(sync_client):
    """Verify POST request to /health returns 405 Method Not Allowed."""
    response = sync_client.post("/health")
    assert response.status_code == 405

def test_health_check_method_mismatch_put(sync_client):
    """Verify PUT request to /health returns 405 Method Not Allowed."""
    response = sync_client.put("/health")
    assert response.status_code == 405

def test_health_check_method_mismatch_delete(sync_client):
    """Verify DELETE request to /health returns 405 Method Not Allowed."""
    response = sync_client.delete("/health")
    assert response.status_code == 405

def test_invalid_health_subpath(sync_client):
    """Verify GET request to invalid subpath of /health returns 404 Not Found."""
    response = sync_client.get("/health/extra")
    assert response.status_code == 404

def test_health_check_headers(sync_client):
    """Verify health check response headers contain application/json."""
    response = sync_client.get("/health")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
