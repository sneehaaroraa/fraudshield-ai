"""
backend/app.py
──────────────
FraudShield AI — FastAPI entry point.

Run locally:
    uvicorn backend.app:app --reload --port 8000

All primary routes are prefixed /api so the Vite proxy forwards them correctly:
    vite.config.js → '/api': 'http://127.0.0.1:8000'

Route map:
    /api/auth/*          → auth_router      (register, login, /me)
    /auth/* and /*       → auth aliases     (register, login compatibility)
    /api/fraud/*         → fraud_routes     (transactions, alerts, predict)
    /api/analytics/*     → analytics_routes (summary, trends, risk-distribution)
    /api/fraud/predict   → ml_routes        (enhanced ML prediction — overrides rule-only version)
    /api/analytics/*     → ml_routes        (trends, risk-distribution, type-risk, model-info)
    /api/health          → inline           (liveness probe)
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from .database.db import init_db
from .routes.auth_router import router as auth_router
from .routes.fraud_routes import router as fraud_router
from .routes.analytics_routes import router as analytics_router
from .routes.ml_routes import router as ml_router

logger = logging.getLogger("fraudshield")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialise SQLite schema (idempotent, safe to call every boot)."""
    logger.info("Starting FraudShield API")
    init_db()

    if os.getenv("AUTO_SEED", "false").lower() == "true":
        from .database.seed_data import seed
        seed()

    yield  # app runs here


app = FastAPI(
    title="FraudShield AI",
    description="Financial Fraud Detection & Cybersecurity Threat Response API",
    version="2.0.0",
    lifespan=lifespan,
)
@app.get("/")
def home():
    return {"message": "FraudShield Backend Running"}

# ── CORS ────────────────────────────────────────────────────────────────────
_frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
_allowed_origins = [
    origin.strip()
    for origin in _frontend_origin.split(",")
    if origin.strip() and origin.strip() != "*"
]
_allow_origin_regex = ".*" if os.getenv("FRONTEND_ORIGIN", "").strip() == "*" else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Error logging ────────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error during %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."},
    )

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth_router,      prefix="/api/auth")         # Phase 2: JWT auth
app.include_router(auth_router,      prefix="/auth")             # Backward-compatible local auth paths
app.include_router(auth_router)                                  # /register and /login aliases
app.include_router(fraud_router,     prefix="/api")              # Phase 3: transactions + alerts
app.include_router(analytics_router, prefix="/api")              # Phase 4: analytics summary
app.include_router(ml_router,        prefix="/api")              # Phase 5: ML predict + analytics

# ── Health probe (for Docker / render.com / Railway) ────────────────────────
@app.get("/api/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "FraudShield AI", "version": "2.0.0"}
