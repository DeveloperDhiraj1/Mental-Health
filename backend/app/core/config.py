from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _origins() -> tuple[str, ...]:
    raw = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500,http://localhost:5173,http://127.0.0.1:5173")
    return tuple(x.strip() for x in raw.split(",") if x.strip())


def _list_env(name: str, default: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in os.getenv(name, default).split(",") if x.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Mental Health Text Signal API")
    environment: str = os.getenv("ENVIRONMENT", "development")
    model_artifact_path: Path | None = Path(os.environ["MODEL_ARTIFACT_PATH"]) if os.getenv("MODEL_ARTIFACT_PATH") else None
    cors_origins: tuple[str, ...] = _origins()
    max_text_chars: int = int(os.getenv("MAX_TEXT_CHARS", "5000"))
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "32"))
    max_request_bytes: int = int(os.getenv("MAX_REQUEST_BYTES", str(16 * 1024 * 1024)))
    allowed_hosts: tuple[str, ...] = _list_env("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver")
    enable_docs: bool = os.getenv("ENABLE_DOCS", "true").lower() in {"1", "true", "yes"}


settings = Settings()
