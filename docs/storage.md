# Private asset storage (S3-compatible)

Set S3_BUCKET, S3_REGION, optional S3_ENDPOINT_URL and AWS credentials via runtime secrets.
Use a **private** bucket, least-privilege credentials, encryption at rest and TLS.

The `PrivateStorage` adapter provides signed uploads, signed reads, server-side output uploads and deletes. It is **not yet exposed as a public upload endpoint**: the Go backend must authorize ownership, consent, image metadata and upload quotas before issuing signed uploads. A signed PUT URL alone does not enforce file size; configure bucket policies and validate the uploaded object before AI processing.

Do not expose provider results as permanent URLs. Download them only from allowlisted provider domains, validate MIME, dimensions and byte size, then store privately.

For Cloudflare R2, server-side encryption headers may differ; validate provider compatibility before deployment. Current `put_image` requests AES256 and may require configuration for R2.

The existing worker remains fail-closed until the trusted asset resolver and provider output ingestion are wired together.
