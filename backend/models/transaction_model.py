"""
Transaction ORM model — maps PaySim dataset columns to a relational table.
Stores raw transaction fields plus computed fraud metadata.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text
)
from sqlalchemy.sql import func
from  database.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # PaySim dataset fields
    step = Column(Integer, nullable=False, comment="Simulation hour (1–743)")
    transaction_type = Column(String(20), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    name_orig = Column(String(50), nullable=False, index=True)
    old_balance_orig = Column(Float, nullable=False)
    new_balance_orig = Column(Float, nullable=False)
    name_dest = Column(String(50), nullable=False, index=True)
    old_balance_dest = Column(Float, nullable=False)
    new_balance_dest = Column(Float, nullable=False)

    # Ground-truth fraud labels from dataset
    is_fraud = Column(Boolean, nullable=False, default=False, index=True)
    is_flagged_fraud = Column(Boolean, nullable=False, default=False)

    # Computed risk fields (populated by risk scoring engine)
    risk_score = Column(Float, nullable=True)
    severity = Column(String(10), nullable=True, index=True)   # LOW/MEDIUM/HIGH/CRITICAL
    fraud_detected = Column(Boolean, nullable=True, default=False)
    risk_explanation = Column(Text, nullable=True)

    # Record metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"<Transaction id={self.id} type={self.transaction_type} "
            f"amount={self.amount:.2f} fraud={self.is_fraud}>"
        )
