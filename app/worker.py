"""Single-node FASHN worker using trusted Supabase object references."""
import asyncio
import logging
import os
import time
from uuid import uuid4

from app.job_store import claim_next, finish, get_job
from app.providers.fashn import FashnProvider
from app.provider_download import fetch_provider_image
from app.storage import PrivateStorage, StorageError

log = logging.getLogger(__name__)

class ProcessingError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code

def _verify_source(storage: PrivateStorage, kind: str, asset_id: str) -> str:
    metadata = storage.head(kind, asset_id)
    if not (0 < metadata.get("ContentLength", 0) <= 10 * 1024 * 1024):
        raise ProcessingError("INVALID_SOURCE_SIZE")
    if metadata.get("ContentType", "").split(";")[0].lower() not in {"image/jpeg", "image/png", "image/webp"}:
        raise ProcessingError("INVALID_SOURCE_TYPE")
    return storage.read_url(kind, asset_id, expires=900)

async def execute_job(job: dict, storage=None, provider=None, downloader=None):
    """Execute only server-authorized asset IDs. Go must enforce asset ownership."""
    storage = storage or PrivateStorage()
    provider = provider or FashnProvider()
    downloader = downloader or fetch_provider_image
    inputs = job["inputs"]
    if job["type"] == "avatar":
        source = _verify_source(storage, "uploads", inputs["image_asset_id"])
        prediction_id = await provider.create_avatar(source)
        output_kind = "avatars"
    elif job["type"] == "tryon":
        model = _verify_source(storage, "avatars", inputs["avatar_asset_id"])
        garment = _verify_source(storage, "garments", inputs["garment_asset_id"])
        prediction_id = await provider.create_tryon(model, garment)
        output_kind = "tryons"
    else:
        raise ProcessingError("UNKNOWN_JOB_TYPE")

    max_wait = int(os.getenv("FASHN_MAX_WAIT_SECONDS", "180"))
    interval = max(1.0, float(os.getenv("FASHN_POLL_SECONDS", "3")))
    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline:
        status = await provider.status(prediction_id)
        state = str(status.get("status", "")).lower()
        if state in ("failed", "canceled", "cancelled"):
            raise ProcessingError("PROVIDER_FAILED")
        if state in ("completed", "succeeded"):
            output = status.get("output")
            url = output[0] if isinstance(output, list) and output else output
            if not isinstance(url, str):
                raise ProcessingError("PROVIDER_OUTPUT_MISSING")
            data, mime = await downloader(url)
            asset_id = str(uuid4())
            storage.put_image(output_kind, asset_id, data, mime)
            return {"asset_id": asset_id, "kind": output_kind}
        await asyncio.sleep(interval)
    raise ProcessingError("PROVIDER_TIMEOUT")

def process_one():
    job_id = claim_next()
    if job_id is None:
        return False
    try:
        result = asyncio.run(execute_job(get_job(job_id)))
        finish(job_id, "succeeded", result=result)
    except ProcessingError as exc:
        finish(job_id, "failed", error_code=exc.code)
    except Exception:
        log.exception("Processing failed for job %s", job_id)
        finish(job_id, "failed", error_code="PROCESSING_FAILED")
    return True

def main():
    logging.basicConfig(level=logging.INFO)
    interval = max(0.5, float(os.getenv("WORKER_POLL_SECONDS", "2")))
    while True:
        if not process_one():
            time.sleep(interval)

if __name__ == "__main__":
    main()
