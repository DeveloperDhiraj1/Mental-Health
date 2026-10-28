from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    available: bool = False
    processed: bool = False
    files_received: int
    message: str
    clinical_use: bool = False
