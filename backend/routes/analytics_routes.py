"""
backend/routes/analytics_routes.py
────────────────────────────────────
GET /api/analytics/summary

Returns aggregated KPIs computed from the live SQLite database.
This is the endpoint AnalyticsTab and useAnalytics() call.

All computation happens here in SQL — the frontend just renders numbers.
No authentication required for Phase 4 (add Depends(get_current_user) in Phase 5).
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..models.transaction_model import Transaction
from ..models.fraud_alert_model import FraudAlert as Alert
from ..services.data_loader import seed_database

router = APIRouter()


def _ensure_seeded(db: Session):
    seed_database(db)


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    """
    Returns a full analytics snapshot from the database.

    Computed fields:
      - total_transactions, total_fraud, fraud_rate_pct
      - total_flagged, total_blocked, total_cleared
      - avg_risk_score
      - open_alerts, critical_alerts, high_alerts
      - by_type:     fraud breakdown per transaction type
      - by_severity: alert count per severity level
      - risk_bands:  transaction count in risk score bands
    """
    _ensure_seeded(db)

    # ── Transaction aggregates ────────────────────────────────────────────────

    tx_totals = db.query(
        func.count(Transaction.id).label("total"),
        func.sum(case((Transaction.is_fraud == True, 1), else_=0)).label("fraud"),
        func.sum(case((Transaction.status == "FLAGGED", 1), else_=0)).label("flagged"),
        func.sum(case((Transaction.status == "BLOCKED", 1), else_=0)).label("blocked"),
        func.sum(case((Transaction.status == "CLEAR",   1), else_=0)).label("cleared"),
        func.round(func.avg(Transaction.risk_score), 1).label("avg_risk"),
    ).one()

    total      = tx_totals.total or 0
    fraud      = tx_totals.fraud or 0
    fraud_rate = round((fraud / total * 100), 4) if total else 0

    # ── Alert aggregates ──────────────────────────────────────────────────────

    alert_totals = db.query(
        func.count(Alert.id).label("total"),
        func.sum(case((Alert.status == "OPEN",         1), else_=0)).label("open"),
        func.sum(case((Alert.severity == "CRITICAL",   1), else_=0)).label("critical"),
        func.sum(case((Alert.severity == "HIGH",       1), else_=0)).label("high"),
    ).one()

    # ── By transaction type ───────────────────────────────────────────────────

    by_type_rows = db.query(
        Transaction.tx_type.label("type"),
        func.count(Transaction.id).label("count"),
        func.sum(case((Transaction.is_fraud == True, 1), else_=0)).label("fraud_count"),
    ).group_by(Transaction.tx_type).all()

    by_type = [
        {
            "type":        r.type,
            "count":       r.count,
            "fraud_count": r.fraud_count or 0,
            "fraud_rate":  round((r.fraud_count or 0) / r.count * 100, 2) if r.count else 0,
        }
        for r in by_type_rows
    ]

    # ── By alert severity ─────────────────────────────────────────────────────

    by_sev_rows = db.query(
        Alert.severity.label("severity"),
        func.count(Alert.id).label("count"),
    ).group_by(Alert.severity).all()

    # Sort in standard SOC severity order
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    by_severity = sorted(
        [{"severity": r.severity, "count": r.count} for r in by_sev_rows],
        key=lambda x: sev_order.get(x["severity"], 9),
    )

    # ── Risk score bands (for histogram) ─────────────────────────────────────

    def band_count(low, high):
        return db.query(func.count(Transaction.id)).filter(
            Transaction.risk_score >= low,
            Transaction.risk_score < high,
        ).scalar() or 0

    risk_bands = [
        {"band": "0–24  (LOW)",      "count": band_count(0,  25)},
        {"band": "25–54 (LOW-MED)",  "count": band_count(25, 55)},
        {"band": "55–69 (MEDIUM)",   "count": band_count(55, 70)},
        {"band": "70–84 (HIGH)",     "count": band_count(70, 85)},
        {"band": "85–99 (CRITICAL)", "count": band_count(85, 100)},
    ]

    # ── Response ──────────────────────────────────────────────────────────────

    return {
        # Transactions
        "total_transactions": total,
        "total_fraud":        fraud,
        "fraud_rate_pct":     fraud_rate,
        "total_flagged":      tx_totals.flagged or 0,
        "total_blocked":      tx_totals.blocked or 0,
        "total_cleared":      tx_totals.cleared or 0,
        "avg_risk_score":     float(tx_totals.avg_risk or 0),

        # Alerts
        "open_alerts":        alert_totals.open     or 0,
        "critical_alerts":    alert_totals.critical or 0,
        "high_alerts":        alert_totals.high     or 0,
        "total_alerts":       alert_totals.total    or 0,

        # Breakdowns
        "by_type":     by_type,
        "by_severity": by_severity,
        "risk_bands":  risk_bands,
    }
