# Dressify AI Service

FastAPI starter for 2D avatar and virtual try-on job orchestration.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INTERNAL_API_TOKEN=local-dev-secret
uvicorn app.main:app --reload --port 8091
pytest -q
```

API documentation: http://localhost:8091/docs

Internal endpoints require `Authorization: Bearer <INTERNAL_API_TOKEN>`:
- `POST /internal/avatars`
- `POST /internal/tryons`
- `GET /internal/jobs/{job_id}`

`GET /health` is public.

**Development only:** run `python -m app.worker` separately with the same `JOB_DB_PATH`. Go must validate user ownership, consent, and uploads before creating internal jobs. See `docs/go-integration.md` and `docs/storage.md`. SQLite lacks crash recovery and production idempotency; do not deploy publicly.
