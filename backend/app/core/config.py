from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _origins() -> tuple[str, ...]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    return tuple(x.strip() for x in raw.split(",") if x.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Mental Health Text Signal API")
    environment: str = os.getenv("ENVIRONMENT", "development")
    model_artifact_path: Path | None = Path(os.environ["MODEL_ARTIFACT_PATH"]) if os.getenv("MODEL_ARTIFACT_PATH") else None
    cors_origins: tuple[str, ...] = _origins()
    max_text_chars: int = int(os.getenv("MAX_TEXT_CHARS", "5000"))
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "32"))


settings = Settings()
