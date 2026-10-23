from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.include_router(router)
