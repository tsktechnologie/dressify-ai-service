"""Internal-only temporary photo ingestion. Go must authenticate users and check consent."""
from uuid import uuid4
from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile
from app.image_validation import InvalidImage, validate_image
from app.job_store import create_job
from app.storage import PrivateStorage

router = APIRouter(prefix="/internal", tags=["Internal image uploads"])
MAX_BYTES = 10 * 1024 * 1024

def _authorize(authorization):
    from app.main import require_token
    require_token(authorization)

@router.post("/avatars/upload", status_code=202)
async def upload_avatar(
    image: UploadFile = File(...),
    consent_version: str = Form(..., min_length=1),
    authorization: str | None = Header(default=None),
):
    _authorize(authorization)
    data = await image.read(MAX_BYTES + 1)
    await image.close()
    try:
        mime = validate_image(data)
    except InvalidImage as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    asset_id = str(uuid4())
    try:
        storage = PrivateStorage()
        storage.put_source("uploads", asset_id, data, mime)
        try:
            job = create_job("avatar", {"image_asset_id": asset_id, "consent_version": consent_version,
                                        "temporary_source": True})
        except Exception:
            storage.delete("uploads", asset_id)
            raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Storage unavailable") from exc
    return job
