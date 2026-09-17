import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["services"]["neo4j"] == "connected"
    assert data["services"]["sqlite"] == "connected"

def test_curriculum_concepts(client):
    response = client.get("/api/v1/curriculum/concepts")
    assert response.status_code == 200
    data = response.json()
    assert "concepts" in data
    assert len(data["concepts"]) >= 6

def test_student_enrollment_and_remediation(client):
    unique_email = "tester.integration@ezitech.org"
    enroll_res = client.post("/api/v1/students", json={
        "name": "Integration Tester",
        "email": unique_email,
        "track_id": "ai_ds",
        "learning_speed": 1.0
    })
    assert enroll_res.status_code in [200, 400]

    students = client.get("/api/v1/students").json()
    student = next(s for s in students if s["email"] == unique_email)
    s_id = student["id"]

    # Ingest a failing score for python_basics
    client.post("/api/v1/students/quiz", json={
        "student_id": s_id,
        "concept_id": "python_basics",
        "score": 0.50
    })

    # Verify knowledge gap blocks data_wrangling
    gap_res = client.get(f"/api/v1/students/{s_id}/knowledge-gap?target_concept_id=data_wrangling")
    assert gap_res.status_code == 200
    gap_data = gap_res.json()
    assert gap_data["ready_for_target"] is False
    assert any(gap["concept_id"] == "python_basics" for gap in gap_data["unmet_prerequisites"])