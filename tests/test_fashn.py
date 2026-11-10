import asyncio
import httpx
from app.providers.fashn import FashnProvider, FashnError

def test_avatar_request_shape():
    async def handler(request):
        assert request.url.path == "/v1/run"
        import json
        payload = json.loads(request.content)
        assert payload["model_name"] == "face-to-model"
        assert payload["inputs"]["face_image"] == "https://assets.example/photo.jpg"
        assert request.headers["authorization"] == "Bearer test-key"
        return httpx.Response(200, json={"id": "prediction-1"})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = FashnProvider(api_key="test-key", client=client)
            assert await provider.create_avatar("https://assets.example/photo.jpg") == "prediction-1"
    asyncio.run(run())

def test_tryon_request_shape_and_status():
    async def handler(request):
        if request.url.path.endswith("/run"):
            import json
            payload = json.loads(request.content)
            assert payload["model_name"] == "tryon-v1.6"
            assert payload["inputs"]["garment_image"] == "https://assets.example/garment.jpg"
            return httpx.Response(200, json={"id": "prediction-2"})
        return httpx.Response(200, json={"id": "prediction-2", "status": "completed", "output": ["https://cdn.example/output.png"]})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = FashnProvider(api_key="test-key", client=client)
            assert await provider.create_tryon("https://assets.example/avatar.jpg", "https://assets.example/garment.jpg") == "prediction-2"
            assert (await provider.status("prediction-2"))["status"] == "completed"
    asyncio.run(run())

def test_missing_key_fails_closed():
    async def run():
        provider = FashnProvider(api_key="")
        try:
            await provider.create_avatar("https://assets.example/photo.jpg")
        except FashnError:
            return
        assert False, "Missing key should fail"
    asyncio.run(run())
