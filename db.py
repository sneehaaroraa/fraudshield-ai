"""
backend/database/db.py
──────────────────────
SQLAlchemy engine + session.

SQLite is used for Phase 1 (zero setup).
Swap to Postgres later by changing DATABASE_URL env var.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fraudshield.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
    echo=False,  # flip to True to see raw SQL in terminal
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """All ORM models inherit from here."""
    pass


def init_db():
    """Register models then create all tables (safe to call multiple times)."""
    from backend.models import transaction, alert  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a DB session per request, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
