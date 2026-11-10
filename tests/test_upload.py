import os
from io import BytesIO
from unittest.mock import patch
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

def test_multipart_avatar_upload(tmp_path, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "test-secret")
    monkeypatch.setenv("JOB_DB_PATH", str(tmp_path / "jobs.sqlite3"))
    saved = []
    class Storage:
        def put_source(self, kind, asset_id, data, mime):
            saved.append((kind, asset_id, mime))
        def delete(self, kind, asset_id):
            pass
    photo = BytesIO()
    Image.new("RGB", (128, 128)).save(photo, "JPEG")
    with patch("app.upload_routes.PrivateStorage", return_value=Storage()):
        response = TestClient(app).post(
            "/internal/avatars/upload",
            headers={"Authorization": "Bearer test-secret"},
            files={"image": ("photo.jpg", photo.getvalue(), "image/jpeg")},
            data={"consent_version": "v1"})
    assert response.status_code == 202, response.text
    assert response.json()["inputs"]["temporary_source"] is True
    assert saved[0][0] == "uploads"

def test_upload_requires_auth():
    response = TestClient(app).post("/internal/avatars/upload")
    assert response.status_code == 401
