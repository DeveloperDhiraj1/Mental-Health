# MindScope AI frontend

This is a React + Vite responsive frontend for the local FastAPI service. It does not store history or fabricate results. Analysis is gated at five valid posts and uses only the verified batch endpoint. The output is non-clinical text-signal research output, not a diagnosis.

## Start locally

Terminal 1, from the project root:

```powershell
$env:CORS_ORIGINS="http://127.0.0.1:5500,http://localhost:5500"
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Terminal 2, from `frontend`:

```powershell
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1 --port 5500
```

To configure another backend origin, copy `.env.example` to `.env` and set `VITE_API_BASE_URL` before starting Vite. The backend accepts 5–32 posts per batch.

Open `http://127.0.0.1:5500`. The current backend has no model artifact, so the workspace will correctly show model unavailable and will not send prediction requests.
