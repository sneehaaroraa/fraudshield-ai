"""
backend/models/__init__.py
──────────────────────────
Registers all ORM models so SQLAlchemy's create_all() picks them up.
Import order matters: User has no foreign keys, Transaction and FraudAlert do.
"""

from backend.models.user import User                          # noqa: F401
from backend.models.transaction_model import Transaction      # noqa: F401
from backend.models.fraud_alert_model import FraudAlert       # noqa: F401

__all__ = ["User", "Transaction", "FraudAlert"]
