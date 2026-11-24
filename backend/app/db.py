from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

from app.core.config import settings

try:
    from pymongo import ASCENDING, DESCENDING, MongoClient
except ImportError:  # SQLite remains usable when the optional Mongo dependency is absent.
    ASCENDING = DESCENDING = MongoClient = None

_mongo_client = None
_mongo_db = None


def _use_mongodb() -> bool:
    backend = settings.database_backend
    if backend not in {"auto", "sqlite", "mongodb"}:
        raise RuntimeError("DATABASE_BACKEND must be one of: auto, sqlite, mongodb")
    return backend == "mongodb" or (backend == "auto" and bool(settings.mongodb_uri))


def database_backend() -> str:
    return "mongodb" if _use_mongodb() else "sqlite"


def _connect() -> sqlite3.Connection:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def _db():
    connection = _connect()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def _mongo_collections():
    if MongoClient is None:
        raise RuntimeError("MongoDB backend requires pymongo; install backend requirements first")
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is required when DATABASE_BACKEND=mongodb")
    global _mongo_client, _mongo_db
    if _mongo_db is None:
        _mongo_client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms, appname="mindscope-ai")
        _mongo_client.admin.command("ping")
        _mongo_db = _mongo_client[settings.mongodb_db_name]
    return _mongo_db["users"], _mongo_db["sessions"], _mongo_db["analysis_requests"]


def close_db() -> None:
    global _mongo_client, _mongo_db
    if _mongo_client is not None:
        _mongo_client.close()
    _mongo_client = None
    _mongo_db = None


def init_db() -> None:
    if _use_mongodb():
        users, sessions, analyses = _mongo_collections()
        users.create_index([("email", ASCENDING)], unique=True, name="uq_users_email")
        sessions.create_index([("token_hash", ASCENDING)], unique=True, name="uq_sessions_token")
        sessions.create_index([("user_id", ASCENDING)], name="idx_sessions_user")
        analyses.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)], name="idx_analysis_user")
        return
    with _db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            expires_at INTEGER NOT NULL,
            revoked_at INTEGER
        );
        CREATE TABLE IF NOT EXISTS analysis_requests (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_count INTEGER NOT NULL,
            model_version TEXT,
            result_json TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_analysis_user ON analysis_requests(user_id, created_at);
        """)


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return "pbkdf2_sha256$310000$" + salt.hex() + "$" + digest.hex()


def verify_password(password: str, encoded: str) -> bool:
    try:
        _, iterations, salt_hex, digest_hex = encoded.split("$")
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def create_user(email: str, password: str) -> dict[str, Any]:
    now = int(time.time())
    user = {"id": str(uuid4()), "email": email.lower().strip(), "role": "user", "is_active": True}
    password_hash = _hash_password(password)
    if _use_mongodb():
        users, _, _ = _mongo_collections()
        users.insert_one({**user, "password_hash": password_hash, "created_at": now})
        return user
    with _db() as db:
        db.execute("INSERT INTO users (id, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)", (user["id"], user["email"], password_hash, "user", now))
    return user


def find_user(email: str) -> dict[str, Any] | None:
    normalized = email.lower().strip()
    if _use_mongodb():
        users, _, _ = _mongo_collections()
        return users.find_one({"email": normalized}, {"_id": 0})
    with _db() as db:
        row = db.execute("SELECT id, email, password_hash, role, is_active FROM users WHERE email = ?", (normalized,)).fetchone()
    return dict(row) if row else None


def create_session(user_id: str) -> tuple[str, int]:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + settings.session_ttl_seconds
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if _use_mongodb():
        _, sessions, _ = _mongo_collections()
        sessions.insert_one({"token_hash": token_hash, "user_id": user_id, "expires_at": expires_at, "revoked_at": None})
    else:
        with _db() as db:
            db.execute("INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)", (token_hash, user_id, expires_at))
    return token, expires_at


def user_from_token(token: str) -> dict[str, Any] | None:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = int(time.time())
    if _use_mongodb():
        users, sessions, _ = _mongo_collections()
        session = sessions.find_one({"token_hash": token_hash, "revoked_at": None, "expires_at": {"$gt": now}}, {"_id": 0})
        if not session:
            return None
        user = users.find_one({"id": session["user_id"]}, {"_id": 0, "id": 1, "email": 1, "role": 1, "is_active": 1})
        return user if user and user.get("is_active", False) else None
    with _db() as db:
        row = db.execute("SELECT u.id, u.email, u.role, u.is_active FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ? AND s.revoked_at IS NULL AND s.expires_at > ?", (token_hash, now)).fetchone()
    return dict(row) if row and row["is_active"] else None


def revoke_session(token: str) -> None:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if _use_mongodb():
        _, sessions, _ = _mongo_collections()
        sessions.update_one({"token_hash": token_hash}, {"$set": {"revoked_at": int(time.time())}})
        return
    with _db() as db:
        db.execute("UPDATE sessions SET revoked_at = ? WHERE token_hash = ?", (int(time.time()), token_hash))


def record_analysis(user_id: str, item_count: int, labels: list[list[str]], model_version: str | None = None) -> str:
    request_id = str(uuid4())
    document = {"id": request_id, "user_id": user_id, "item_count": item_count, "model_version": model_version, "result_json": labels, "created_at": int(time.time())}
    if _use_mongodb():
        _, _, analyses = _mongo_collections()
        analyses.insert_one(document)
        return request_id
    with _db() as db:
        db.execute("INSERT INTO analysis_requests (id, user_id, item_count, model_version, result_json, created_at) VALUES (?, ?, ?, ?, ?, ?)", (request_id, user_id, item_count, model_version, json.dumps(labels), document["created_at"]))
    return request_id


def list_analysis(user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    safe_limit = min(max(limit, 1), 100)
    if _use_mongodb():
        _, _, analyses = _mongo_collections()
        rows = analyses.find({"user_id": user_id}, {"_id": 0, "id": 1, "item_count": 1, "model_version": 1, "created_at": 1}).sort("created_at", DESCENDING).limit(safe_limit)
        return list(rows)
    with _db() as db:
        rows = db.execute("SELECT id, item_count, model_version, created_at FROM analysis_requests WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, safe_limit)).fetchall()
    return [dict(row) for row in rows]
