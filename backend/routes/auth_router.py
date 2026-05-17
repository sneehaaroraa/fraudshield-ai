"""
backend/routes/auth_router.py
──────────────────────────────
POST /api/auth/register  → create account, return JWT
POST /api/auth/login     → verify credentials, return JWT
GET  /api/auth/me        → return profile of logged-in user (protected)

Password flow:
  register → bcrypt.hash(plain) → stored in DB
  login    → bcrypt.verify(plain, hash) → issue JWT if match
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from backend.database.db import get_db
from backend.models.user import User
from backend.auth.jwt_handler import create_access_token, get_current_user

router  = APIRouter()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

VALID_ROLES = {"admin", "analyst", "auditor"}


# ── Request / Response schemas ────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email:    EmailStr
    name:     str
    password: str
    role:     str = "analyst"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f"Role must be one of: {VALID_ROLES}")
        return v


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class UserOut(BaseModel):
    """What we send back to the frontend — never includes password."""
    email: str
    name:  str
    role:  str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserOut


# ── Helper ────────────────────────────────────────────────────────────────────

def _token_response(user: User) -> dict:
    """Build the standard token + user payload returned after auth."""
    token = create_access_token({
        "sub":  user.email,
        "name": user.name,
        "role": user.role,
    })
    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {"email": user.email, "name": user.name, "role": user.role},
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Returns a JWT immediately so the user is logged in right after registering.
    """
    # Prevent duplicate emails (case-insensitive)
    existing = db.query(User).filter(User.email == body.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email           = body.email.lower(),
        name            = body.name.strip(),
        hashed_password = pwd_ctx.hash(body.password),
        role            = body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Verify email + password and issue a JWT.
    Uses a constant-time compare (bcrypt.verify) to prevent timing attacks.
    """
    user = db.query(User).filter(User.email == body.email.lower()).first()

    # Always run pwd_ctx.verify even when user not found — prevents timing attacks
    # that could reveal which emails are registered
    dummy_hash = "$2b$12$invalidhashfortimingprotectiononly000000000000000000000000"
    stored_hash = user.hashed_password if user else dummy_hash

    if not pwd_ctx.verify(body.password, stored_hash) or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled. Contact your administrator.",
        )

    return _token_response(user)


@router.get("/me")
def me(current: dict = Depends(get_current_user)):
    """
    Protected endpoint — returns the profile of the logged-in user.
    Frontend calls this on app load to rehydrate the session from a stored token.
    """
    return {
        "email": current["sub"],
        "name":  current.get("name", "Analyst"),
        "role":  current.get("role", "analyst"),
    }
