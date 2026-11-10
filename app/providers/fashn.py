"""FASHN API adapter. No user images or API keys are logged."""
import os
import httpx

BASE_URL = "https://api.fashn.ai/v1"

class FashnError(RuntimeError):
    pass

class FashnProvider:
    def __init__(self, api_key: str | None = None, client: httpx.AsyncClient | None = None):
        self.api_key = api_key or os.getenv("FASHN_API_KEY", "")
        self.client = client

    def _headers(self):
        if not self.api_key:
            raise FashnError("FASHN_API_KEY is not configured")
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, payload: dict | None = None):
        async def call(client):
            try:
                response = await client.request(method, BASE_URL + path, headers=self._headers(), json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise FashnError("Unexpected FASHN response")
                return data
            except (httpx.HTTPError, ValueError) as exc:
                raise FashnError("FASHN request failed") from exc
        if self.client is not None:
            return await call(self.client)
        async with httpx.AsyncClient() as client:
            return await call(client)

    async def create_avatar(self, face_image: str) -> str:
        data = await self._request("POST", "/run", {
            "model_name": "face-to-model",
            "inputs": {"face_image": face_image, "output_format": "jpeg"}
        })
        if not data.get("id"):
            raise FashnError("FASHN did not return a prediction id")
        return data["id"]

    async def create_tryon(self, model_image: str, garment_image: str) -> str:
        data = await self._request("POST", "/run", {
            "model_name": "tryon-v1.6",
            "inputs": {"model_image": model_image, "garment_image": garment_image, "category": "auto"}
        })
        if not data.get("id"):
            raise FashnError("FASHN did not return a prediction id")
        return data["id"]

    async def status(self, prediction_id: str) -> dict:
        if not prediction_id or not all(c.isalnum() or c in "-_" for c in prediction_id):
            raise ValueError("Invalid prediction id")
        return await self._request("GET", f"/status/{prediction_id}")
