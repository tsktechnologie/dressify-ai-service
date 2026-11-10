# FASHN adapter integration

The adapter in `app/providers/fashn.py` implements documented FASHN `POST /v1/run` and `GET /v1/status/{id}` requests.

- Avatar: experimental `face-to-model`, which produces an **upper-body** image from a face reference. It does not guarantee full-body or biometric likeness.
- Try-on: stable `tryon-v1.6`, using a model/person image and garment image.
- The adapter is isolated from HTTP routes intentionally. Existing API requests carry **asset IDs**, not signed URLs. A trusted server-side asset resolver, persistent job store and background worker must be built before enabling real generation.
- Provider output URLs must be copied into private Dressify storage before expiry; never expose long-lived provider URLs as user assets.
- Never accept arbitrary client-supplied URLs for provider fetching. Restrict source assets to server-controlled storage.
- Never commit FASHN_API_KEY; inject it as a secret in the worker environment.
- MockTransport tests validate request shapes without sending images or incurring API charges.

References:
https://docs.fashn.ai/api-reference/face-to-model
https://docs.fashn.ai/api-reference/tryon-v1-6
https://docs.fashn.ai/guides/tryon-python-quickstart-guide
