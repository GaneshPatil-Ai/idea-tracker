"""Tests for the /health endpoint."""

from fastapi.testclient import TestClient


def test_health_check_returns_200_and_healthy(client: TestClient) -> None:
    """GET /health should return 200 OK and status information."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "Idea Tracker"
    assert data["database"] == "healthy"
    assert "version" in data
