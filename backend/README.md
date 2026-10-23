# Experimental API

This backend exposes health/model-availability endpoints and a guarded prediction interface. No compatible trained artifact currently exists, so prediction requests return HTTP 503 rather than fabricated output.

## Run from the project root

```powershell
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Endpoints:

- `GET /health`
- `GET /api/v1/model/info`
- `POST /api/v1/predictions`
- `POST /api/v1/predictions/batch`

Configure `MODEL_ARTIFACT_PATH` only after a compatible, approved model artifact exists. Keep CORS origins explicit. This is experimental text classification, not diagnosis or clinical risk prediction.
