# Go backend integration contract (required before public release)

The AI service is **internal only**. Go authenticates Dressify users, verifies consent and checks ownership of every source asset before calling Python.

## Proposed Go endpoints
- `POST /v1/ai/avatars`: authorize authenticated user and uploaded photo; send internal `POST /internal/avatars`.
- `POST /v1/ai/tryons`: authorize ownership of avatar and permission to use garment; send internal `POST /internal/tryons`.
- `GET /v1/ai/jobs/{id}`: verify the job belongs to requesting user before proxying sanitized status.
- `GET /v1/ai/assets/{id}/download`: authorize and return a short-lived signed read URL.
- `DELETE /v1/ai/avatars/{id}`: delete avatar and dependent assets according to policy.

**Important:** Python's current shared bearer token authenticates a *service*, not a user. Its internal job status endpoint is not user-scoped. Never expose the Python service to the internet or proxy job lookups without user-to-job ownership checks in Go.

Go must maintain an ownership mapping for `job_id`, `asset_id`, `user_id` and consent version. Reject asset IDs not owned by the caller. Generated output IDs must be registered to the same user.

Uploads should be allocated server-side and verified by Go. Supabase bucket must remain private. Never expose Supabase S3 credentials or FASHN API keys to the mobile app.

## Operational limits
The SQLite queue is a development-only single-node implementation. It does not recover abandoned `processing` jobs, coordinate distributed workers or guarantee exactly-once provider charges. Add a Postgres-backed queue with leases, idempotency and retry limits before production. Worker currently blocks during provider polling and needs durable prediction IDs to resume safely after crashes.

The face-to-model provider is experimental and may not create the full-body avatar desired by the product. Validate output quality, cost and API response schemas with real non-sensitive test assets before enabling.
