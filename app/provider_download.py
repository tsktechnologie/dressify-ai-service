"""Download provider output without arbitrary URL fetching or redirects."""
import os
from urllib.parse import urlsplit
import httpx
from app.image_validation import validate_image

class UnsafeProviderOutput(ValueError):
    pass

def _allowed(url: str) -> bool:
    parts = urlsplit(url)
    allowed = {h.strip().lower() for h in os.getenv("FASHN_OUTPUT_HOSTS", "cdn.fashn.ai").split(",") if h.strip()}
    return parts.scheme == "https" and parts.hostname in allowed and not parts.username and not parts.password and parts.port in (None, 443)

async def fetch_provider_image(url: str, client: httpx.AsyncClient | None = None):
    if not _allowed(url):
        raise UnsafeProviderOutput("Untrusted provider output host")
    async def fetch(c):
        async with c.stream("GET", url, follow_redirects=False, timeout=30) as response:
            if response.status_code != 200:
                raise UnsafeProviderOutput("Provider output unavailable")
            data = bytearray()
            async for chunk in response.aiter_bytes():
                data.extend(chunk)
                if len(data) > 10 * 1024 * 1024:
                    raise UnsafeProviderOutput("Provider output too large")
            mime = validate_image(bytes(data))
            return bytes(data), mime
    if client is not None:
        return await fetch(client)
    async with httpx.AsyncClient(trust_env=False) as c:
        return await fetch(c)
