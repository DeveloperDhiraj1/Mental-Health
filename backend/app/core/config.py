from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _path_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _origins() -> tuple[str, ...]:
    raw = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500,http://localhost:5173,http://127.0.0.1:5173")
    return tuple(x.strip() for x in raw.split(",") if x.strip())


def _list_env(name: str, default: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in os.getenv(name, default).split(",") if x.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Mental Health Text Signal API")
    environment: str = os.getenv("ENVIRONMENT", "development")
    model_artifact_path: Path | None = _path_env("MODEL_ARTIFACT_PATH", PROJECT_ROOT / "models" / "model.joblib") if os.getenv("MODEL_ARTIFACT_PATH") else None
    cors_origins: tuple[str, ...] = _origins()
    max_text_chars: int = int(os.getenv("MAX_TEXT_CHARS", "5000"))
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "32"))
    max_request_bytes: int = int(os.getenv("MAX_REQUEST_BYTES", str(16 * 1024 * 1024)))
    allowed_hosts: tuple[str, ...] = _list_env("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver")
    enable_docs: bool = os.getenv("ENABLE_DOCS", "true").lower() in {"1", "true", "yes"}
    database_path: Path = _path_env("DATABASE_PATH", PROJECT_ROOT / "backend" / "data" / "mindscope.db")
    database_backend: str = os.getenv("DATABASE_BACKEND", "auto").strip().lower()
    mongodb_uri: str = os.getenv("MONGODB_URI", "").strip()
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "mindscope_ai").strip() or "mindscope_ai"
    mongodb_server_selection_timeout_ms: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "3000"))
    auth_required: bool = os.getenv("AUTH_REQUIRED", "false").lower() in {"1", "true", "yes"} or environment == "production"
    session_ttl_seconds: int = int(os.getenv("SESSION_TTL_SECONDS", "86400"))
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))


settings = Settings()
