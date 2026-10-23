from fastapi import APIRouter, HTTPException, Request, status

from app.core.exceptions import ModelUnavailableError
from app.schemas.prediction import BatchPredictionRequest, PredictionRequest, PredictionResponse

router = APIRouter()


def _error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No compatible model artifact is available; predictions are disabled")


@router.post("/api/v1/predictions", response_model=PredictionResponse)
def prediction(request: Request, payload: PredictionRequest) -> PredictionResponse:
    service = request.app.state.prediction_service
    try:
        labels = service.predict([payload.text])[0]
    except ModelUnavailableError as exc:
        raise _error() from exc
    return PredictionResponse(available=True, message="Experimental text classification only", labels=labels)


@router.post("/api/v1/predictions/batch", response_model=list[PredictionResponse])
def batch_prediction(request: Request, payload: BatchPredictionRequest) -> list[PredictionResponse]:
    service = request.app.state.prediction_service
    try:
        labels = service.predict(payload.texts)
    except ModelUnavailableError as exc:
        raise _error() from exc
    return [PredictionResponse(available=True, message="Experimental text classification only", labels=row) for row in labels]
