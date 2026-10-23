from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/api/v1/model/info")
def model_info(request: Request) -> dict:
    return request.app.state.prediction_service.info
