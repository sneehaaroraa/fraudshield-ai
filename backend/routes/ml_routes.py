"""
backend/routes/ml_routes.py
────────────────────────────
ML-powered endpoints added on top of existing routes.

New routes:
  GET  /analytics/trends            — fraud trends over time
  GET  /analytics/risk-distribution — risk score histogram with fraud overlay
  GET  /analytics/type-risk         — per-type risk breakdown
  GET  /analytics/model-info        — trained model metadata
  POST /fraud/predict               — enhanced ML prediction (replaces rule-only version)

Note: POST /fraud/predict is registered here and will override the one in
fraud_routes.py — include this router AFTER fraud_routes in app.py.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from ..database.db import get_db
from ..services.fraud_prediction_service import fraud_predictor
from ..services.ml_analytics_service import MLAnalyticsService

router = APIRouter(tags=["ML Analytics"])

_ml_analytics = MLAnalyticsService()


# ── Analytics: Trends ────────────────────────────────────────────────────────

@router.get("/analytics/trends")
def get_fraud_trends(
    buckets: int = 20,
    db: Session = Depends(get_db),
):
    """
    Fraud trends aggregated over transaction time steps.
    Returns total, fraud_count, fraud_rate, avg_risk per time bucket.
    """
    return _ml_analytics.get_fraud_trends(db, buckets=buckets)


# ── Analytics: Risk Distribution ─────────────────────────────────────────────

@router.get("/analytics/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    """
    Risk score distribution in 10-point bands with fraud/legitimate split.
    Use for histogram chart on the analytics dashboard.
    """
    return _ml_analytics.get_risk_distribution(db)


# ── Analytics: Type Risk Breakdown ───────────────────────────────────────────

@router.get("/analytics/type-risk")
def get_type_risk(db: Session = Depends(get_db)):
    """Per transaction type: fraud rate, avg risk score, total volume."""
    return _ml_analytics.get_type_risk_breakdown(db)


# ── Analytics: Model Info ────────────────────────────────────────────────────

@router.get("/analytics/model-info")
def get_model_info():
    """
    Returns metadata about the trained ML model including:
    - training metrics (AUC, precision, recall, F1)
    - feature importances
    - training sample size
    """
    return fraud_predictor.get_model_info()


# ── ML Predict (enhanced) ────────────────────────────────────────────────────

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


@router.post("/fraud/predict")
def ml_predict_fraud(body: MLPredictRequest):
    """
    Enhanced ML fraud prediction.
    Uses trained RandomForest model (falls back to rules if not trained).

    Returns:
      - fraud_detected: bool
      - risk_score: 0-100
      - confidence_score: 0-1 (model probability)
      - severity: LOW | MEDIUM | HIGH | CRITICAL
      - explanation: human-readable reasoning
      - ml_used: whether ML model was applied
    """
    result = fraud_predictor.predict(body.model_dump())
    return {
        "input": body.model_dump(),
        **result,
    }
