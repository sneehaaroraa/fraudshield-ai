"""
backend/services/data_loader.py
────────────────────────────────
Loads transactions.json from the data/ folder and seeds the SQLite DB.

Why a service instead of reading the file in the route?
  - Routes stay thin (just HTTP logic)
  - Seeding logic is reusable and testable
  - Later: replace with a real DB ingestion pipeline
"""

from __future__ import annotations
import json
from pathlib import Path

from sqlalchemy.orm import Session

from backend.models.transaction_model import Transaction
from backend.models.fraud_alert_model import FraudAlert as Alert
from backend.fraud_engine.scorer import score

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "transactions.json"


def load_raw() -> list[dict]:
    """Read transactions.json from disk."""
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH) as f:
        return json.load(f)


def seed_database(db: Session, max_rows: int = 5000) -> int:
    """
    Seed the transactions table from transactions.json.
    Skips rows that already exist (idempotent — safe to call multiple times).

    Returns the number of new rows inserted.
    """
    # Skip if already seeded
    if db.query(Transaction).count() > 0:
        return 0

    rows = load_raw()[:max_rows]
    inserted = 0
    alert_counter = 1

    for raw in rows:
        result = score(raw)
        tx = Transaction(
            tx_id      = raw["id"],
            tx_type    = raw["type"],
            amount     = raw["amount"],
            orig       = raw["orig"],
            dest       = raw["dest"],
            old_bal    = raw.get("oldBal", 0),
            new_bal    = raw.get("newBal", 0),
            is_fraud   = bool(raw.get("isFraud", 0)),
            risk_score = result["risk_score"],
            status     = result["status"],
            rules_hit  = ",".join(result["rules"]),
        )
        db.add(tx)
        inserted += 1

        # Create an alert for every high-risk transaction
        if result["risk_score"] >= 55:
            alert = Alert(
                alert_id   = f"ALT-{alert_counter:04d}",
                alert_type = f"{raw['type']} Fraud Pattern",
                severity   = result["severity"],
                risk_score = result["risk_score"],
                mitre      = ", ".join(result["mitre"]) or "N/A",
                status     = "OPEN",
                tx_id      = raw["id"],
            )
            db.add(alert)
            alert_counter += 1

    db.commit()
    return inserted
