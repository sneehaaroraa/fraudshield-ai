"""
fraud_routes.py

FastAPI router for all /fraud/* endpoints.

Routes:
    GET  /fraud/transactions         — paginated, filtered, sorted transaction list
    GET  /fraud/transactions/{id}    — single transaction detail
    GET  /fraud/alerts               — paginated alert list with status/severity filter
    GET  /fraud/alerts/{id}          — single alert detail
    PATCH /fraud/alerts/{id}/status  — analyst status transition
    POST /fraud/predict              — on-demand risk score for an ad-hoc transaction
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from backend.database.db import get_db
from backend.services.transaction_service import TransactionService
from backend.services.alert_service import AlertService
from backend.fraud_engine.risk_scoring_engine import RiskScoringEngine

router = APIRouter(prefix="/fraud", tags=["Fraud"])

_tx_service = TransactionService()
_alert_service = AlertService()
_risk_engine = RiskScoringEngine()


# -----------------------------------------------------------------------
# Pydantic schemas
# -----------------------------------------------------------------------

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


# -----------------------------------------------------------------------
# Transaction endpoints
# -----------------------------------------------------------------------

@router.get("/transactions")
def list_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    transaction_type: Optional[str] = Query(None, description="Filter by type: PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN"),
    fraud_only: bool = Query(False, description="Return only fraud-detected transactions"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    search: Optional[str] = Query(None, description="Search by account name (origin or destination)"),
    sort_by: str = Query("id", description="Column to sort by"),
    sort_order: str = Query("asc", description="Sort direction: asc or desc"),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    return _tx_service.get_transactions(
        db,
        page=page,
        page_size=page_size,
        transaction_type=transaction_type,
        fraud_only=fraud_only,
        severity=severity,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        min_amount=min_amount,
        max_amount=max_amount,
    )


@router.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = _tx_service.get_transaction_by_id(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


# -----------------------------------------------------------------------
# Alert endpoints
# -----------------------------------------------------------------------

@router.get("/alerts")
def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status: OPEN, INVESTIGATING, ESCALATED, RESOLVED"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    sort_order: str = Query("desc", description="Sort by created_at: asc or desc"),
    db: Session = Depends(get_db),
):
    return _alert_service.get_alerts(
        db,
        page=page,
        page_size=page_size,
        status=status,
        severity=severity,
        sort_order=sort_order,
    )


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = _alert_service.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/alerts/{alert_id}/status")
def update_alert_status(
    alert_id: int,
    body: AlertStatusUpdate,
    db: Session = Depends(get_db),
):
    from backend.models.fraud_alert_model import AlertStatus
    if body.status not in AlertStatus.ALL:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {AlertStatus.ALL}",
        )
    alert, error = _alert_service.update_alert_status(
        db,
        alert_id=alert_id,
        new_status=body.status,
        analyst_notes=body.analyst_notes,
        assigned_to=body.assigned_to,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return alert


# -----------------------------------------------------------------------
# On-demand prediction endpoint
# -----------------------------------------------------------------------

@router.post("/predict")
def predict_fraud(body: PredictRequest):
    """
    Score an ad-hoc transaction without persisting it.
    Useful for testing or real-time pre-submission checks.
    """
    result = _risk_engine.score(body.model_dump())
    return {
        "input": body.model_dump(),
        "risk_score": result["risk_score"],
        "severity": result["severity"],
        "fraud_detected": result["fraud_detected"],
        "explanation": result["explanation"],
    }
