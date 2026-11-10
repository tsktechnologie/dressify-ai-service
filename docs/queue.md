# Queue MVP

The HTTP API uses SQLite-backed durable jobs. Run a **separate** worker:

```bash
export INTERNAL_API_TOKEN=local-dev-secret
export JOB_DB_PATH=./dressify_jobs.sqlite3
uvicorn app.main:app --port 8091
# in a second terminal, same JOB_DB_PATH
python -m app.worker
```

The worker currently **fails closed** with `ASSET_RESOLVER_NOT_CONFIGURED`. It does not call FASHN, because the public API receives asset IDs and must not interpret arbitrary user input as provider-fetchable URLs.

Before real processing: implement authenticated asset lookup and short-lived provider-accessible signed URLs, private output ingestion, provider status polling, timeout handling, cancellation, retry policies, crash recovery and retention/deletion. SQLite is only suitable for local/single-node development. Do not use this implementation as a distributed production queue.
