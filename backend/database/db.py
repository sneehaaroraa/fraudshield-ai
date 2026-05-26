"""
Database engine and session factory.
SQLite for local dev; swap DATABASE_URL env var for Postgres in production.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fraudshield.db")

# connect_args only needed for SQLite (disables same-thread check)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yields a DB session and closes it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist. Called once on startup."""
    # Import models so SQLAlchemy registers them before create_all
    from ..models import transaction_model, fraud_alert_model, user  # noqa: F401
    Base.metadata.create_all(bind=engine)
