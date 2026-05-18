"""
analytics_service.py

Aggregation queries powering the /analytics/summary endpoint.
Returns all data the dashboard needs in a single call to minimise
round-trips from the frontend.
"""

from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from backend.models.transaction_model import Transaction
from backend.models.fraud_alert_model import FraudAlert, AlertStatus


class AnalyticsService:
    """Builds the analytics summary payload from the database."""

    def get_summary(self, db: Session) -> dict:
        return {
            "overview": self._overview(db),
            "fraud_by_type": self._fraud_by_type(db),
            "severity_distribution": self._severity_distribution(db),
            "transaction_volume_by_type": self._volume_by_type(db),
            "alert_status_breakdown": self._alert_status_breakdown(db),
            "top_risk_transactions": self._top_risk_transactions(db),
            "average_risk_score_by_type": self._avg_risk_by_type(db),
        }

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------

    @staticmethod
    def _overview(db: Session) -> dict:
        total_tx = db.query(func.count(Transaction.id)).scalar() or 0
        total_fraud = (
            db.query(func.count(Transaction.id))
            .filter(Transaction.fraud_detected == True)  # noqa: E712
            .scalar()
            or 0
        )
        total_amount = db.query(func.sum(Transaction.amount)).scalar() or 0.0
        fraud_amount = (
            db.query(func.sum(Transaction.amount))
            .filter(Transaction.fraud_detected == True)  # noqa: E712
            .scalar()
            or 0.0
        )
        open_alerts = (
            db.query(func.count(FraudAlert.id))
            .filter(FraudAlert.status == AlertStatus.OPEN)
            .scalar()
            or 0
        )
        avg_risk = db.query(func.avg(Transaction.risk_score)).scalar() or 0.0

        fraud_rate = round((total_fraud / total_tx * 100), 4) if total_tx else 0.0

        return {
            "total_transactions": total_tx,
            "total_fraud_detected": total_fraud,
            "fraud_rate_percent": fraud_rate,
            "total_transaction_amount": round(float(total_amount), 2),
            "total_fraud_amount": round(float(fraud_amount), 2),
            "open_alerts": open_alerts,
            "average_risk_score": round(float(avg_risk), 2),
        }

    @staticmethod
    def _fraud_by_type(db: Session) -> list[dict]:
        rows = (
            db.query(
                Transaction.transaction_type,
                func.count(Transaction.id).label("total"),
                func.sum(
                    case((Transaction.fraud_detected == True, 1), else_=0)  # noqa: E712
                ).label("fraud_count"),
            )
            .group_by(Transaction.transaction_type)
            .all()
        )
        result = []
        for tx_type, total, fraud_count in rows:
            fraud_count = fraud_count or 0
            result.append(
                {
                    "transaction_type": tx_type,
                    "total": total,
                    "fraud_count": fraud_count,
                    "fraud_rate_percent": round(fraud_count / total * 100, 2) if total else 0.0,
                }
            )
        return sorted(result, key=lambda x: x["fraud_count"], reverse=True)

    @staticmethod
    def _severity_distribution(db: Session) -> list[dict]:
        rows = (
            db.query(Transaction.severity, func.count(Transaction.id).label("count"))
            .filter(Transaction.severity.isnot(None))
            .group_by(Transaction.severity)
            .all()
        )
        order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return sorted(
            [{"severity": sev, "count": cnt} for sev, cnt in rows],
            key=lambda x: order.get(x["severity"], 99),
        )

    @staticmethod
    def _volume_by_type(db: Session) -> list[dict]:
        rows = (
            db.query(
                Transaction.transaction_type,
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("total_amount"),
                func.avg(Transaction.amount).label("avg_amount"),
            )
            .group_by(Transaction.transaction_type)
            .all()
        )
        return [
            {
                "transaction_type": tx_type,
                "count": cnt,
                "total_amount": round(float(total or 0), 2),
                "avg_amount": round(float(avg or 0), 2),
            }
            for tx_type, cnt, total, avg in rows
        ]

    @staticmethod
    def _alert_status_breakdown(db: Session) -> list[dict]:
        rows = (
            db.query(FraudAlert.status, func.count(FraudAlert.id).label("count"))
            .group_by(FraudAlert.status)
            .all()
        )
        return [{"status": status, "count": cnt} for status, cnt in rows]

    @staticmethod
    def _top_risk_transactions(db: Session, limit: int = 10) -> list[dict]:
        rows = (
            db.query(Transaction)
            .filter(Transaction.risk_score.isnot(None))
            .order_by(Transaction.risk_score.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": tx.id,
                "transaction_type": tx.transaction_type,
                "amount": tx.amount,
                "risk_score": tx.risk_score,
                "severity": tx.severity,
                "name_orig": tx.name_orig,
                "name_dest": tx.name_dest,
            }
            for tx in rows
        ]

    @staticmethod
    def _avg_risk_by_type(db: Session) -> list[dict]:
        rows = (
            db.query(
                Transaction.transaction_type,
                func.avg(Transaction.risk_score).label("avg_risk"),
                func.max(Transaction.risk_score).label("max_risk"),
            )
            .group_by(Transaction.transaction_type)
            .all()
        )
        return [
            {
                "transaction_type": tx_type,
                "avg_risk_score": round(float(avg or 0), 2),
                "max_risk_score": round(float(mx or 0), 2),
            }
            for tx_type, avg, mx in rows
        ]
