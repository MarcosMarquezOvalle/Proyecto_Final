from __future__ import annotations

import os
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "orders-service-jwt-secret-key-32chars",
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

bearer_scheme = HTTPBearer(auto_error=False)


def _database_path() -> Path:
    configured = os.getenv("ORDER_DB_PATH")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / "orders.db"


def _ensure_user_table() -> None:
    with sqlite3.connect(_database_path()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123"),
        )
        connection.commit()


def create_access_token(subject: str) -> str:
    _ensure_user_table()
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def authenticate_user(username: str, password: str) -> str | None:
    _ensure_user_table()
    with sqlite3.connect(_database_path()) as connection:
        row = connection.execute(
            "SELECT password FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row is None or row[0] != password:
        return None
    return username


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    username = payload.get("sub")
    if not isinstance(username, str) or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username
