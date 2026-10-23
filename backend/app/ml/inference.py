from __future__ import annotations

from app.core.exceptions import ModelUnavailableError
from app.ml.model_loader import ModelLoader


def predict(loader: ModelLoader, texts: list[str]) -> list[list[str]]:
    if not loader.available:
        raise ModelUnavailableError("No compatible trained model artifact is available")
    return loader.predict(texts)
