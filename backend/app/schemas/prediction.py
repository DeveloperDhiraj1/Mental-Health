from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def non_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must contain non-whitespace characters")
        return value


class BatchPredictionRequest(BaseModel):
    texts: list[str] = Field(..., min_length=5, max_length=32)

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, values: list[str]) -> list[str]:
        if len(values) < 5:
            raise ValueError("texts must contain at least 5 posts")
        if any(not x.strip() for x in values):
            raise ValueError("texts must not contain empty or whitespace-only values")
        if any(len(x) > 5000 for x in values):
            raise ValueError("each text must be at most 5000 characters")
        return values


class PredictionResponse(BaseModel):
    available: bool
    experimental: bool = True
    message: str
    labels: list[str] | None = None
