import os
os.environ["INTERNAL_API_TOKEN"] = "test-secret"
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-secret"}

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_auth_required():
    assert client.post("/internal/avatars", json={"image_asset_id":"a","consent_version":"v1"}).status_code == 401

def test_avatar_job():
    response = client.post("/internal/avatars", headers=AUTH, json={"image_asset_id":"a","consent_version":"v1"})
    assert response.status_code == 202
    job = client.get("/internal/jobs/" + response.json()["id"], headers=AUTH)
    assert job.json()["status"] == "queued"

def test_tryon_job():
    response = client.post("/internal/tryons", headers=AUTH, json={"avatar_asset_id":"a","garment_asset_id":"b"})
    assert response.status_code == 202
    assert response.json()["type"] == "tryon"
