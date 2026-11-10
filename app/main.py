from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
import os

from app.job_store import create_job, get_job

app = FastAPI(title="Dressify AI Service", version="0.1.0")

class AvatarRequest(BaseModel):
    image_asset_id: str = Field(min_length=1)
    consent_version: str = Field(min_length=1)

class TryonRequest(BaseModel):
    avatar_asset_id: str = Field(min_length=1)
    garment_asset_id: str = Field(min_length=1)

def require_token(authorization: str | None):
    expected = os.getenv("INTERNAL_API_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Internal token not configured")
    import secrets
    if not authorization or not secrets.compare_digest(authorization, f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/internal/avatars", status_code=202)
def create_avatar(body: AvatarRequest, authorization: str | None = Header(default=None)):
    require_token(authorization)
    return create_job("avatar", body.model_dump())

@app.post("/internal/tryons", status_code=202)
def create_tryon(body: TryonRequest, authorization: str | None = Header(default=None)):
    require_token(authorization)
    return create_job("tryon", body.model_dump())

@app.get("/internal/jobs/{job_id}")
def get_job(job_id: str, authorization: str | None = Header(default=None)):
    require_token(authorization)
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

from app.upload_routes import router as upload_router
app.include_router(upload_router)
