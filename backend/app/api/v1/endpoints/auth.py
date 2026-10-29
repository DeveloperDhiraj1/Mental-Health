from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth import current_user, required_user
from app.db import create_session, create_user, find_user, list_analysis, revoke_session, verify_password
from app.schemas.auth import AuthRequest, AuthResponse, HistoryItem, UserResponse

router = APIRouter(prefix="/api/v1/auth")


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: AuthRequest) -> AuthResponse:
    if find_user(payload.email):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    try:
        user = create_user(payload.email, payload.password)
    except Exception as exc:
        raise HTTPException(status_code=409, detail="Could not create account") from exc
    token, expires_at = create_session(user["id"])
    return AuthResponse(access_token=token, expires_at=expires_at, user=UserResponse(**user))


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest) -> AuthResponse:
    user = find_user(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="This account is disabled")
    token, expires_at = create_session(user["id"])
    return AuthResponse(access_token=token, expires_at=expires_at, user=UserResponse(id=user["id"], email=user["email"], role=user["role"]))


@router.get("/me", response_model=UserResponse)
def me(user: dict = Depends(required_user)) -> UserResponse:
    return UserResponse(id=user["id"], email=user["email"], role=user["role"])


@router.post("/logout")
def logout(request: Request, user: dict | None = Depends(current_user)) -> dict:
    authorization = request.headers.get("Authorization", "")
    if user and authorization.lower().startswith("bearer "):
        revoke_session(authorization[7:].strip())
    return {"ok": True}


@router.get("/history", response_model=list[HistoryItem])
def history(user: dict = Depends(required_user)) -> list[HistoryItem]:
    return [HistoryItem(**item) for item in list_analysis(user["id"])]
