"""
backend/routes/alerts.py
──────────────────────────
GET  /api/fraud/alerts          — list all alerts (filterable by severity/status)
GET  /api/fraud/alerts/{id}     — single alert detail
PATCH /api/fraud/alerts/{id}    — update status (OPEN → INVESTIGATING → ESCALATED → RESOLVED)

Replaces the hardcoded 3-alert array in the old Express server
with real DB-backed alerts generated from the PaySim dataset.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.alert import Alert
from backend.services.data_loader import seed_database

router = APIRouter()

VALID_STATUSES = {"OPEN", "INVESTIGATING", "ESCALATED", "RESOLVED"}


def _ensure_seeded(db: Session):
    seed_database(db)


@router.get("/alerts")
def get_alerts(
    db:       Session = Depends(get_db),
    severity: str     = Query("ALL"),
    status:   str     = Query("ALL"),
    page:     int     = Query(1, ge=1),
    page_size: int    = Query(20, ge=1, le=100, alias="pageSize"),
):
    _ensure_seeded(db)

    q = db.query(Alert)

    if severity != "ALL":
        q = q.filter(Alert.severity == severity)
    if status != "ALL":
        q = q.filter(Alert.status == status)

    total      = q.count()
    total_pages = max(1, -(-total // page_size))
    rows       = q.order_by(Alert.risk_score.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [_fmt(a) for a in rows],
        "pagination": {"page": page, "pageSize": page_size, "total": total, "totalPages": total_pages},
    }


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _fmt(alert)


@router.patch("/alerts/{alert_id}")
def update_alert(alert_id: str, body: dict, db: Session = Depends(get_db)):
    """
    Update alert status or notes.
    Body: { "status": "INVESTIGATING", "notes": "Reviewing..." }
    """
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    new_status = body.get("status")
    if new_status and new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Use: {VALID_STATUSES}")

    if new_status:
        alert.status = new_status
    if "notes" in body:
        alert.notes = body["notes"]

    db.commit()
    db.refresh(alert)
    return _fmt(alert)


def _fmt(a: Alert) -> dict:
    """Serialize an Alert ORM object to a JSON-safe dict."""
    return {
        "id":         a.alert_id,
        "type":       a.alert_type,
        "sev":        a.severity,
        "score":      a.risk_score,
        "mitre":      a.mitre,
        "status":     a.status,
        "txId":       a.tx_id,
        "notes":      a.notes,
        "createdAt":  a.created_at.isoformat() if a.created_at else None,
    }
