"""
backend/app.py
──────────────
FraudShield AI — FastAPI entry point.

Run locally:
    uvicorn backend.app:app --reload --port 8000

All routes are prefixed /api so the Vite proxy forwards them correctly:
    vite.config.js → '/api': 'http://127.0.0.1:8000'

Route map:
    /api/auth/*          → auth_router      (register, login, /me)
    /api/fraud/*         → fraud_routes     (transactions, alerts, predict)
    /api/analytics/*     → analytics_routes (summary, trends, risk-distribution)
    /api/fraud/predict   → ml_routes        (enhanced ML prediction — overrides rule-only version)
    /api/analytics/*     → ml_routes        (trends, risk-distribution, type-risk, model-info)
    /api/health          → inline           (liveness probe)
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from routes.auth_router import router as auth_router
from routes.fraud_routes import router as fraud_router
from routes.analytics_routes import router as analytics_router
from routes.ml_routes import router as ml_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialise SQLite schema (idempotent, safe to call every boot)."""
    init_db()

    if os.getenv("AUTO_SEED", "false").lower() == "true":
        from backend.database.seed_data import seed
        seed()

    yield  # app runs here


app = FastAPI(
    title="FraudShield AI",
    description="Financial Fraud Detection & Cybersecurity Threat Response API",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        os.getenv("FRONTEND_ORIGIN", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth_router,      prefix="/api/auth")         # Phase 2: JWT auth
app.include_router(fraud_router,     prefix="/api")              # Phase 3: transactions + alerts
app.include_router(analytics_router, prefix="/api")              # Phase 4: analytics summary
app.include_router(ml_router,        prefix="/api")              # Phase 5: ML predict + analytics

# ── Health probe (for Docker / render.com / Railway) ────────────────────────
@app.get("/api/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "FraudShield AI", "version": "2.0.0"}
