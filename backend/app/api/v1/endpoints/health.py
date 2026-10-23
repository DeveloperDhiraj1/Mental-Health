from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict:
    service = request.app.state.prediction_service
    return {"status": "ok", "model_available": service.loader.available, "experimental": True}
