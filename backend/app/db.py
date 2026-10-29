from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.config import settings


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


def init_db() -> None:
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
    user = {"id": str(uuid4()), "email": email.lower().strip(), "role": "user", "is_active": True}
    with _db() as db:
        db.execute("INSERT INTO users (id, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)", (user["id"], user["email"], _hash_password(password), "user", int(time.time())))
    return user


def find_user(email: str) -> dict[str, Any] | None:
    with _db() as db:
        row = db.execute("SELECT id, email, password_hash, role, is_active FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
    return dict(row) if row else None


def create_session(user_id: str) -> tuple[str, int]:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + settings.session_ttl_seconds
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with _db() as db:
        db.execute("INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)", (token_hash, user_id, expires_at))
    return token, expires_at


def user_from_token(token: str) -> dict[str, Any] | None:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with _db() as db:
        row = db.execute(
            "SELECT u.id, u.email, u.role, u.is_active FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ? AND s.revoked_at IS NULL AND s.expires_at > ?",
            (token_hash, int(time.time())),
        ).fetchone()
    return dict(row) if row and row["is_active"] else None


def revoke_session(token: str) -> None:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with _db() as db:
        db.execute("UPDATE sessions SET revoked_at = ? WHERE token_hash = ?", (int(time.time()), token_hash))


def record_analysis(user_id: str, item_count: int, labels: list[list[str]], model_version: str | None = None) -> str:
    request_id = str(uuid4())
    with _db() as db:
        db.execute("INSERT INTO analysis_requests (id, user_id, item_count, model_version, result_json, created_at) VALUES (?, ?, ?, ?, ?, ?)", (request_id, user_id, item_count, model_version, json.dumps(labels), int(time.time())))
    return request_id


def list_analysis(user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    with _db() as db:
        rows = db.execute("SELECT id, item_count, model_version, created_at FROM analysis_requests WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, min(max(limit, 1), 100))).fetchall()
    return [dict(row) for row in rows]
