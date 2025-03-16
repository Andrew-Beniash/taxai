from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test that the root endpoint returns a 200 status code."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "AI-Powered Tax Law Application API is running"

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
