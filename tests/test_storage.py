import pytest
from app.storage import PrivateStorage, StorageError

class FakeS3:
    def __init__(self):
        self.calls = []
    def generate_presigned_url(self, operation, Params, ExpiresIn):
        self.calls.append((operation, Params, ExpiresIn))
        return "https://storage.example/signed"
    def put_object(self, **kwargs):
        self.calls.append(("put", kwargs))
    def head_object(self, **kwargs):
        self.calls.append(("head", kwargs))
        return {"ContentLength": 4, "ContentType": "image/jpeg"}
    def delete_object(self, **kwargs):
        self.calls.append(("delete", kwargs))

def test_private_storage(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "test-private")
    fake = FakeS3()
    storage = PrivateStorage(client=fake)
    assert storage.read_url("uploads", "asset_123").startswith("https://")
    assert fake.calls[0][1]["Key"] == "uploads/asset_123"
    storage.put_image("avatars", "avatar_123", b"test", "image/jpeg")
    assert fake.calls[-1][1]["ContentType"] == "image/jpeg"
    assert storage.head("avatars", "avatar_123")["ContentLength"] == 4

def test_rejects_path_traversal(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "test-private")
    storage = PrivateStorage(client=FakeS3())
    with pytest.raises(StorageError):
        storage.read_url("uploads", "../secret")
    with pytest.raises(StorageError):
        storage.upload_url("avatars", "x")
