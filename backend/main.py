"""
main.py — FraudShield AI FastAPI application entry point.

Phase 1: Core backend foundation
Phase 2: JWT authentication
Phase 3: Fraud APIs, transaction database, alert system (current)

Startup sequence:
  1. Initialise SQLite schema (create_all is idempotent)
  2. Register all API routers
  3. Optionally seed the database on first run (set AUTO_SEED=true)
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.db import init_db

# Existing Phase-2 routers (preserve as-is)
# from backend.routes.auth_routes import router as auth_router   ← already registered

# Phase-3 routers
from backend.routes.fraud_routes import router as fraud_router
from backend.routes.analytics_routes import router as analytics_router

app = FastAPI(
    title="FraudShield AI",
    description="Financial fraud detection and SIEM analytics platform",
    version="3.0.0",
)

# CORS — allow the Vite dev server and production build
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev
        "http://localhost:3000",
        os.getenv("FRONTEND_ORIGIN", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create tables and optionally seed data on first boot."""
    init_db()

    if os.getenv("AUTO_SEED", "false").lower() == "true":
        from backend.database.seed_data import seed
        seed()


# -----------------------------------------------------------------------
# Register routers
# -----------------------------------------------------------------------

# NOTE: Uncomment the auth router import once you confirm existing path:
# app.include_router(auth_router)

app.include_router(fraud_router)
app.include_router(analytics_router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "FraudShield AI", "phase": 3}
