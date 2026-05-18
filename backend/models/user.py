"""
backend/models/user.py
──────────────────────
Users table. Passwords are NEVER stored plain — only bcrypt hashes.

Roles:
  admin   → full access (can see all endpoints)
  analyst → default; can view + score transactions
  auditor → read-only; compliance views only
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from  database.db import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    email            = Column(String, unique=True, index=True, nullable=False)
    name             = Column(String, nullable=False)
    hashed_password  = Column(String, nullable=False)          # bcrypt hash
    role             = Column(String, default="analyst")       # admin | analyst | auditor
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
