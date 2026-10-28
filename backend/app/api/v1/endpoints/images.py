from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.schemas.image import ImageUploadResponse

router = APIRouter()

MAX_IMAGE_FILES = 10
MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAGIC = {
    "image/jpeg": lambda data: data.startswith(b"\xff\xd8\xff"),
    "image/png": lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
    "image/webp": lambda data: data.startswith(b"RIFF") and data[8:12] == b"WEBP",
}


@router.post("/api/v1/image-analysis", response_model=ImageUploadResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def image_analysis(files: list[UploadFile] = File(...)) -> ImageUploadResponse:
    if not files:
        raise HTTPException(status_code=422, detail="At least one image is required")
    if len(files) > MAX_IMAGE_FILES:
        raise HTTPException(status_code=413, detail=f"At most {MAX_IMAGE_FILES} images may be uploaded")

    for upload in files:
        if upload.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WebP images are supported")
        content = await upload.read(MAX_IMAGE_BYTES + 1)
        if len(content) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="Each image must be 5 MB or smaller")
        if not MAGIC[upload.content_type](content):
            raise HTTPException(status_code=415, detail="The uploaded file content does not match its image type")
        try:
            with Image.open(BytesIO(content)) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise HTTPException(status_code=415, detail="The uploaded file is not a valid image") from exc
        finally:
            await upload.close()

    return ImageUploadResponse(
        files_received=len(files),
        message="Images were validated, but this text-only project has no vision model or OCR pipeline. No image classification was performed.",
    )
