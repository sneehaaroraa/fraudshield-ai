"""
backend/models/schemas.py
─────────────────────────
Central repository for all Pydantic schemas (Request/Response models).
Used across routes for validation and documentation.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator

# ── Auth Schemas ─────────────────────────────────────────────────────────────

VALID_ROLES = {"admin", "analyst", "auditor"}

class UserOut(BaseModel):
    """What we send back to the frontend — never includes password."""
    email: str
    name:  str
    role:  str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserOut


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


# ── Fraud & Transaction Schemas ──────────────────────────────────────────────

class PredictRequest(BaseModel):
    transaction_type: str = Field(..., examples=["TRANSFER"])
    amount: float = Field(..., gt=0)
    old_balance_orig: float = Field(..., ge=0)
    new_balance_orig: float = Field(..., ge=0)
    old_balance_dest: float = Field(..., ge=0)
    new_balance_dest: float = Field(..., ge=0)
    name_orig: str = Field(default="C000000000")
    name_dest: str = Field(default="C999999999")
    is_fraud: bool = Field(default=False)
    is_flagged_fraud: bool = Field(default=False)


class AlertStatusUpdate(BaseModel):
    status: str = Field(..., examples=["INVESTIGATING"])
    analyst_notes: Optional[str] = None
    assigned_to: Optional[str] = None


# ── ML Schemas ───────────────────────────────────────────────────────────────

class MLPredictRequest(BaseModel):
    transaction_type: str = Field(..., examples=["TRANSFER"])
    amount: float = Field(..., gt=0)
    old_balance_orig: float = Field(default=0.0, ge=0)
    new_balance_orig: float = Field(default=0.0, ge=0)
    old_balance_dest: float = Field(default=0.0, ge=0)
    new_balance_dest: float = Field(default=0.0, ge=0)
    name_orig: str = Field(default="C000000000")
    name_dest: str = Field(default="C999999999")
    step: int = Field(default=1, ge=1)
    is_fraud: bool = Field(default=False)
    is_flagged_fraud: bool = Field(default=False)
