"""
backend/routes/transactions.py
────────────────────────────────
GET  /api/fraud/transactions  — paginated, filterable transaction list
POST /api/fraud/predict       — score a single transaction on the fly

Mirrors the existing Express server's /api/transactions endpoint
so the frontend works without any changes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.database.db import get_db, init_db
from backend.models.transaction import Transaction
from backend.services.data_loader import seed_database
from backend.fraud_engine.scorer import score

router = APIRouter()


def _ensure_seeded(db: Session):
    """Seed on first request if the table is empty."""
    seed_database(db)


@router.get("/transactions")
def get_transactions(
    db:        Session = Depends(get_db),
    search:    str     = Query("", description="Search by tx_id, orig, or dest"),
    tx_type:   str     = Query("ALL", alias="type"),
    status:    str     = Query("ALL"),
    fraud_only: bool   = Query(False,  alias="fraudOnly"),
    page:      int     = Query(1,      ge=1),
    page_size: int     = Query(12,     ge=1, le=50, alias="pageSize"),
):
    """
    Returns paginated transactions with optional filters.
    Response shape matches the existing Express server so
    the frontend hooks work without modification.
    """
    _ensure_seeded(db)

    q = db.query(Transaction)

    if search:
        s = f"%{search.upper()}%"
        q = q.filter(or_(
            Transaction.tx_id.ilike(s),
            Transaction.orig.ilike(s),
            Transaction.dest.ilike(s),
        ))

    if tx_type != "ALL":
        q = q.filter(Transaction.tx_type == tx_type)

    if status != "ALL":
        q = q.filter(Transaction.status == status)

    if fraud_only:
        q = q.filter(Transaction.is_fraud == True)  # noqa: E712

    total      = q.count()
    total_pages = max(1, -(-total // page_size))   # ceiling division
    rows       = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [
            {
                "id":        r.tx_id,
                "type":      r.tx_type,
                "amount":    r.amount,
                "orig":      r.orig,
                "dest":      r.dest,
                "oldBal":    r.old_bal,
                "newBal":    r.new_bal,
                "isFraud":   int(r.is_fraud),
                "riskScore": r.risk_score,
                "status":    r.status,
                "rules":     r.rules_hit.split(",") if r.rules_hit else [],
            }
            for r in rows
        ],
        "pagination": {
            "page":       page,
            "pageSize":   page_size,
            "total":      total,
            "totalPages": total_pages,
        },
    }


@router.post("/predict")
def predict(body: dict, db: Session = Depends(get_db)):
    """Score a single transaction submitted from the frontend Risk Engine tab."""
    result = score(body)
    from datetime import datetime, timezone
    return {**result, "analyzedAt": datetime.now(timezone.utc).isoformat()}
