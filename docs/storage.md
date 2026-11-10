# Supabase Storage integration

Use Supabase Storage's S3-compatible endpoint with the existing boto3 adapter.

## Supabase setup
1. Create a **private** bucket named `dressify-ai` in the Supabase dashboard.
2. Enable S3 access and generate S3 access credentials from Supabase Storage settings.
3. Configure the service secrets (never commit actual credentials):

```dotenv
S3_BUCKET=dressify-ai
S3_ENDPOINT_URL=https://YOUR_PROJECT_REF.storage.supabase.co/storage/v1/s3
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

Confirm the endpoint and region displayed in your Supabase project settings; use those values if different.

## Layout
- `uploads/{asset_id}`: original authorized photo
- `garments/{asset_id}`: garment source image
- `avatars/{asset_id}`: generated avatar
- `tryons/{asset_id}`: generated try-on result

Keys are validated to avoid path traversal. The adapter supports short-lived signed GET/PUT URLs, HEAD metadata checks, private output writes and deletes.

## Security
- S3 credentials stay on the server only; do not place them in Expo or public environment variables.
- The Go backend must authenticate the user and authorize each asset before issuing upload or download permissions.
- Signed PUT requests alone do not enforce file size. Validate stored object length, MIME and decoded image bytes before processing.
- Avoid long-lived public object URLs. Provider-facing URLs should be short-lived.
- Enforce consent, retention, cleanup, quotas, rate limiting and access auditing.
- Verify Supabase S3 endpoint behavior for signed URLs and deployment-specific policies.
- The worker is intentionally fail-closed until server-authorized asset ownership and safe output ingestion are implemented.

## Local checks
`pytest -q` runs mocked storage tests. Live tests require an actual Supabase project, private bucket and secrets.
