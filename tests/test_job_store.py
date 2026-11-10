from app import job_store

def test_durable_queue(tmp_path, monkeypatch):
    monkeypatch.setenv("JOB_DB_PATH", str(tmp_path / "jobs.db"))
    job = job_store.create_job("avatar", {"image_asset_id": "image-1"})
    assert job_store.get_job(job["id"])["status"] == "queued"
    assert job_store.claim_next() == job["id"]
    assert job_store.claim_next() is None
    job_store.finish(job["id"], "failed", error_code="ASSET_RESOLVER_NOT_CONFIGURED")
    assert job_store.get_job(job["id"])["error_code"] == "ASSET_RESOLVER_NOT_CONFIGURED"
