from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router
from app.core.config import settings
from app.ml.model_loader import ModelLoader
from app.services.prediction_service import PredictionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    loader = ModelLoader(settings.model_artifact_path)
    loader.load()
    app.state.prediction_service = PredictionService(loader)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Experimental non-clinical linguistic-signal API; not a diagnostic system.",
    lifespan=lifespan,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "X-Request-ID"])
app.include_router(router)


@app.middleware("http")
async def production_guards(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > settings.max_request_bytes:
        response = JSONResponse(status_code=413, content={"detail": "Request body is too large"})
    else:
        response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response
