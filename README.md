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

**Prototype only:** jobs are stored in process memory and remain queued. No actual AI images are generated. Before production: add persistent storage, queue workers, signed assets, rate limits, provider integration, and deletion flows.
