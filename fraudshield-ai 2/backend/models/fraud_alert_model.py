"""
FraudAlert ORM model — one alert per flagged transaction.
Supports analyst triage workflow: OPEN → INVESTIGATING → ESCALATED → RESOLVED.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.db import Base


class AlertStatus:
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"

    ALL = [OPEN, INVESTIGATING, ESCALATED, RESOLVED]


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Link to the triggering transaction
    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Alert metadata
    severity = Column(String(10), nullable=False, index=True)   # LOW/MEDIUM/HIGH/CRITICAL
    fraud_reason = Column(Text, nullable=False)
    risk_score = Column(Float, nullable=False)

    # Analyst workflow
    status = Column(String(20), nullable=False, default=AlertStatus.OPEN, index=True)
    analyst_notes = Column(Text, nullable=True)
    assigned_to = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship (lazy load to avoid N+1 on list endpoints)
    transaction = relationship("Transaction", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<FraudAlert id={self.id} tx={self.transaction_id} "
            f"severity={self.severity} status={self.status}>"
        )
