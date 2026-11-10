# Hybrid avatar upload — development integration

The new internal `POST /internal/avatars/upload` accepts `multipart/form-data` with:
- `image` (JPEG/PNG/WebP, 64x64 minimum, 10 MB maximum, 30 MP maximum)
- `consent_version` (required nonempty string)

It requires `Authorization: Bearer <INTERNAL_API_TOKEN>`. The service validates image bytes, stores a UUID-named temporary source in the private Supabase bucket under `uploads/`, and creates a queued avatar job. The worker reads a short-lived signed source URL, calls FASHN, validates and saves the output under `avatars/`, and deletes the temporary source on terminal success or failure.

For local tests, run API and worker with identical `JOB_DB_PATH`, and configure Supabase S3 credentials and FASHN_API_KEY. The Postman collection includes multipart upload and job status polling.

## Production blockers
- **Go integration not implemented:** Go must authenticate the user, obtain explicit consent, rate limit uploads, enforce per-user quotas, and store job/asset ownership before proxying to this internal endpoint. Python service must remain private.
- The current SQLite worker has no durable leases, retries, or crash recovery. If a worker crashes, source uploads can remain in storage. Implement a scheduled retention sweeper for abandoned temporary files and jobs.
- The FASHN output host allowlist and prediction response shapes require verification with the real provider; do not loosen URL checks blindly.
- Uploading via Go proxy can increase Go memory usage unless it streams with strict limits.
- No persistent user-to-avatar ownership table, deletion API, or explicit consent audit exists yet.
- Generated assets are not automatically associated with the Go user profile.
- A production image moderation check is not wired into this flow.
- Verify S3 endpoint/credentials and FASHN provider API in staging before real-user use.
