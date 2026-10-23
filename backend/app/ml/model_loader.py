from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib


class ModelLoader:
    def __init__(self, artifact_path: Path | None):
        self.artifact_path = artifact_path
        self.model: Any | None = None
        self.error: str | None = None

    @property
    def available(self) -> bool:
        return self.model is not None

    def load(self) -> None:
        if self.artifact_path is None:
            self.error = "No MODEL_ARTIFACT_PATH configured"
            return
        if not self.artifact_path.is_file():
            self.error = "Configured model artifact does not exist"
            return
        try:
            self.model = joblib.load(self.artifact_path)
        except Exception:
            self.error = "Configured model artifact could not be loaded"
            self.model = None

    def predict(self, texts: list[str]) -> list[list[str]]:
        if not self.available:
            raise RuntimeError("Model artifact is unavailable")
        predictions = self.model.predict(texts)
        return [list(row) if hasattr(row, "__iter__") and not isinstance(row, str) else [str(row)] for row in predictions]
