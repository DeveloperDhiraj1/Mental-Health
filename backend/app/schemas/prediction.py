from pydantic import BaseModel, Field, field_validator
from app.core.config import settings


class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=settings.max_text_chars)

    @field_validator("text")
    @classmethod
    def non_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must contain non-whitespace characters")
        return value


class BatchPredictionRequest(BaseModel):
    texts: list[str] = Field(..., min_length=5, max_length=settings.max_batch_size)

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, values: list[str]) -> list[str]:
        if len(values) < 5:
            raise ValueError("texts must contain at least 5 posts")
        if any(not x.strip() for x in values):
            raise ValueError("texts must not contain empty or whitespace-only values")
        if any(len(x) > settings.max_text_chars for x in values):
            raise ValueError(f"each text must be at most {settings.max_text_chars} characters")
        return values


class PredictionResponse(BaseModel):
    available: bool
    experimental: bool = True
    message: str
    labels: list[str] | None = None
