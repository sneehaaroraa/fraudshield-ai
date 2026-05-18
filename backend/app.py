"""
backend/app.py
──────────────
FraudShield AI — FastAPI entry point.

Run locally:
    uvicorn backend.app:app --reload --port 8000

All routes are prefixed /api so the Vite proxy needs one change:
    '/api': 'http://127.0.0.1:8000'
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database.db import init_db
from backend.routes import health, transactions, alerts, auth_router, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()   # create SQLite tables on first boot (now includes users table)
    yield


app = FastAPI(
    title="FraudShield AI",
    description="Financial Fraud Detection & Cybersecurity Threat Response API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router,  prefix="/api/auth")
app.include_router(health.router,       prefix="/api")
app.include_router(transactions.router, prefix="/api/fraud")
app.include_router(alerts.router,       prefix="/api/fraud")
app.include_router(analytics.router,    prefix="/api/analytics")   # ← Phase 4
