"""
analytics_routes.py

FastAPI router for all /analytics/* endpoints.

Routes:
    GET /analytics/summary — full dashboard aggregation payload
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

_analytics_service = AnalyticsService()


@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Returns a single aggregated payload containing:
    - Overview KPIs (total transactions, fraud rate, open alerts, avg risk)
    - Fraud counts broken down by transaction type
    - Severity distribution (CRITICAL / HIGH / MEDIUM / LOW)
    - Transaction volume and amounts by type
    - Alert status breakdown (OPEN / INVESTIGATING / ESCALATED / RESOLVED)
    - Top 10 highest-risk transactions
    - Average and max risk score per transaction type
    """
    return _analytics_service.get_summary(db)
