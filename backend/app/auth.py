from fastapi import Depends, HTTPException, Request, status

from app.core.config import settings
from app.db import user_from_token


def _token(request: Request) -> str | None:
    value = request.headers.get("Authorization", "")
    if value.lower().startswith("bearer "):
        return value[7:].strip()
    return None


def current_user(request: Request) -> dict | None:
    user = user_from_token(_token(request)) if _token(request) else None
    if user is None and settings.auth_required:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def required_user(user: dict | None = Depends(current_user)) -> dict:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def required_admin(user: dict = Depends(required_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return user
