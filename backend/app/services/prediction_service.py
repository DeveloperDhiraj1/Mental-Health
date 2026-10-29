from app.core.exceptions import ModelUnavailableError
from app.ml.inference import predict
from app.ml.model_loader import ModelLoader


class PredictionService:
    def __init__(self, loader: ModelLoader):
        self.loader = loader

    @property
    def info(self) -> dict:
        return {
            "available": self.loader.available,
            "artifact_configured": self.loader.artifact_path is not None,
            "status": "ready" if self.loader.available else "unavailable",
            "experimental": True,
            "clinical_use": False,
            "message": "Experimental text classification only; not a medical diagnosis or clinical risk assessment.",
        }

    def predict(self, texts: list[str]) -> list[list[str]]:
        try:
            return predict(self.loader, texts)
        except ModelUnavailableError:
            raise
