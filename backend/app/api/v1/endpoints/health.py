from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict:
    service = request.app.state.prediction_service
    return {"status": "ok", "model_available": service.loader.available, "experimental": True}


@router.get("/ready")
def ready(request: Request) -> dict:
    service = request.app.state.prediction_service
    if not service.loader.available:
        raise HTTPException(status_code=503, detail="Service is not ready: no compatible model artifact is available")
    return {"status": "ready", "model_available": True, "experimental": True}
