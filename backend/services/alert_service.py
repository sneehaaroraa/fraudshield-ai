"""
alert_service.py

Business logic for fraud alert retrieval and analyst workflow transitions.
Status machine: OPEN → INVESTIGATING → ESCALATED → RESOLVED
"""

from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.fraud_alert_model import FraudAlert, AlertStatus
from ..models.transaction_model import Transaction


# Valid one-way status transitions
ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    AlertStatus.OPEN: [AlertStatus.INVESTIGATING, AlertStatus.RESOLVED],
    AlertStatus.INVESTIGATING: [AlertStatus.ESCALATED, AlertStatus.RESOLVED],
    AlertStatus.ESCALATED: [AlertStatus.RESOLVED],
    AlertStatus.RESOLVED: [],
}


class AlertService:
    """Handles fraud alert queries and analyst status transitions."""

    def get_alerts(
        self,
        db: Session,
        *,
        page: int = 1,
        page_size: int = 25,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        sort_order: str = "desc",
    ) -> dict:
        query = db.query(FraudAlert)

        if status:
            query = query.filter(FraudAlert.status == status.upper())

        if severity:
            query = query.filter(FraudAlert.severity == severity.upper())

        direction = desc if sort_order.lower() == "desc" else lambda c: c
        query = query.order_by(direction(FraudAlert.created_at))

        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        total_pages = max(1, (total + page_size - 1) // page_size)

        return {
            "items": [self._serialize(alert, db) for alert in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def get_alert_by_id(self, db: Session, alert_id: int) -> Optional[dict]:
        alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
        return self._serialize(alert, db) if alert else None

    def update_alert_status(
        self,
        db: Session,
        alert_id: int,
        new_status: str,
        analyst_notes: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> tuple[Optional[dict], Optional[str]]:
        """
        Transition alert status.
        Returns (serialized_alert, error_message).
        """
        alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
        if not alert:
            return None, "Alert not found"

        allowed = ALLOWED_TRANSITIONS.get(alert.status, [])
        if new_status not in allowed:
            return None, (
                f"Cannot transition from {alert.status} to {new_status}. "
                f"Allowed: {allowed or ['none']}"
            )

        alert.status = new_status
        if analyst_notes:
            alert.analyst_notes = analyst_notes
        if assigned_to:
            alert.assigned_to = assigned_to
        if new_status == AlertStatus.RESOLVED:
            from sqlalchemy.sql import func
            alert.resolved_at = func.now()

        db.commit()
        db.refresh(alert)
        return self._serialize(alert, db), None

    # ------------------------------------------------------------------
    # Serialiser
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize(alert: FraudAlert, db: Session) -> dict:
        # Fetch linked transaction summary without eager-loading all fields
        tx = db.query(Transaction).filter(Transaction.id == alert.transaction_id).first()
        tx_summary = None
        if tx:
            tx_summary = {
                "id": tx.id,
                "transaction_type": tx.transaction_type,
                "amount": tx.amount,
                "name_orig": tx.name_orig,
                "name_dest": tx.name_dest,
                "risk_score": tx.risk_score,
            }

        return {
            "id": alert.id,
            "transaction_id": alert.transaction_id,
            "severity": alert.severity,
            "fraud_reason": alert.fraud_reason,
            "risk_score": alert.risk_score,
            "status": alert.status,
            "analyst_notes": alert.analyst_notes,
            "assigned_to": alert.assigned_to,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "transaction": tx_summary,
        }
