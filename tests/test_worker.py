import asyncio
from app.worker import execute_job, ProcessingError

class Storage:
    def __init__(self):
        self.saved = []
    def head(self, kind, asset_id):
        return {"ContentLength": 1024, "ContentType": "image/jpeg"}
    def read_url(self, kind, asset_id, expires):
        return "https://storage.example/signed"
    def put_image(self, kind, asset_id, data, mime):
        self.saved.append((kind, asset_id, data, mime))

class Provider:
    def __init__(self, fail=False):
        self.fail = fail
    async def create_avatar(self, image):
        assert image == "https://storage.example/signed"
        return "prediction1"
    async def create_tryon(self, model, garment):
        assert model == garment == "https://storage.example/signed"
        return "prediction2"
    async def status(self, prediction_id):
        return {"status": "failed" if self.fail else "completed",
                "output": ["https://cdn.fashn.ai/output.jpg"]}

async def download(url):
    assert url == "https://cdn.fashn.ai/output.jpg"
    return b"image-bytes", "image/jpeg"

def test_avatar_job_persists_output():
    storage = Storage()
    result = asyncio.run(execute_job(
        {"type": "avatar", "inputs": {"image_asset_id": "photo1"}},
        storage=storage, provider=Provider(), downloader=download))
    assert result["kind"] == "avatars"
    assert storage.saved[0][0] == "avatars"

def test_tryon_job_persists_output():
    storage = Storage()
    result = asyncio.run(execute_job(
        {"type": "tryon", "inputs": {"avatar_asset_id": "avatar1", "garment_asset_id": "garment1"}},
        storage=storage, provider=Provider(), downloader=download))
    assert result["kind"] == "tryons"
    assert storage.saved[0][0] == "tryons"

def test_provider_failure():
    try:
        asyncio.run(execute_job(
            {"type": "avatar", "inputs": {"image_asset_id": "photo1"}},
            storage=Storage(), provider=Provider(fail=True), downloader=download))
    except ProcessingError as exc:
        assert exc.code == "PROVIDER_FAILED"
    else:
        assert False, "Expected ProcessingError"
