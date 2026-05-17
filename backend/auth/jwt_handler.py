"""
backend/auth/jwt_handler.py
───────────────────────────
JWT token creation, verification, and FastAPI dependency guards.

How it works:
  1. On login/register → create_access_token() signs a JWT with user data
  2. Frontend stores it (localStorage or sessionStorage)
  3. On every protected request → Authorization: Bearer <token> header
  4. get_current_user() dependency decodes & validates the token
  5. require_role() lets you restrict endpoints to specific roles

Set SECRET_KEY in .env before deploying — default is insecure.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# ── Config ────────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production-use-long-random-key")
ALGORITHM  = "HS256"
EXPIRE_MIN = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

# FastAPI reads the Bearer token from the Authorization header automatically
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Token creation ────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Sign a JWT containing `data` + an expiry timestamp.

    Example data:
        {"sub": "analyst@example.com", "role": "analyst", "name": "Alice"}
    """
    payload = data.copy()
    expire  = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=EXPIRE_MIN))
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ── Token verification ────────────────────────────────────────────────────────

def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT.
    Raises HTTP 401 if token is invalid, expired, or tampered with.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise ValueError("Missing subject")
        return payload
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── FastAPI dependencies ──────────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Inject into any route to require authentication.

    Usage:
        @router.get("/protected")
        def my_route(user = Depends(get_current_user)):
            return {"hello": user["name"]}
    """
    return decode_token(token)


def require_role(*roles: str):
    """
    Factory that returns a dependency enforcing one of the given roles.

    Usage:
        @router.delete("/admin-only")
        def admin_route(user = Depends(require_role("admin"))):
            ...
    """
    def _guard(current: dict = Depends(get_current_user)):
        if current.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {list(roles)}. Your role: {current.get('role')}",
            )
        return current
    return _guard
