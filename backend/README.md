# Experimental API

This backend exposes health/model-availability endpoints and a guarded prediction interface. No compatible trained artifact currently exists, so prediction requests return HTTP 503 rather than fabricated output.

## Run from the project root

```powershell
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Endpoints:

- `GET /health`
- `GET /ready` (returns 503 until a compatible model is loaded)
- `GET /api/v1/model/info`
- `POST /api/v1/predictions`
- `POST /api/v1/predictions/batch`
- `POST /api/v1/image-analysis` with multipart field `files` (JPEG, PNG, or WebP; up to 10 files, 5 MB each). Files are validated in memory and not persisted. The endpoint currently returns an explicit unsupported-processing response because the project has no vision model or OCR pipeline.

Configure `MODEL_ARTIFACT_PATH` only after a compatible, approved model artifact exists. Keep CORS origins explicit. This is experimental text classification, not diagnosis or clinical risk prediction.

## Production configuration

Set these environment variables in the deployment secret/config store:

`ENVIRONMENT=production`
`MODEL_ARTIFACT_PATH=<approved artifact path>`
`CORS_ORIGINS=https://your-frontend.example`
`ALLOWED_HOSTS=api.example.com`
`ENABLE_DOCS=false`
`MAX_REQUEST_BYTES=16777216`

Run behind an HTTPS reverse proxy with authentication, rate limiting, monitoring, and a process manager. The application intentionally does not log raw post text.
