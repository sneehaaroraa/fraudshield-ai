"""
seed_data.py — One-time seeder.

Reads paysim_working.csv, scores every transaction through the risk engine,
bulk-inserts into SQLite, and creates FraudAlerts for every flagged row.

Usage:
    python -m backend.database.seed_data
"""

import csv
import os
import sys
import time
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from  database.db import SessionLocal, init_db
from  models.transaction_model import Transaction
from  models.fraud_alert_model import FraudAlert, AlertStatus
from  fraud_engine.risk_scoring_engine import RiskScoringEngine

CSV_PATH = Path(__file__).resolve().parents[2] / "paysim_working.csv"
BATCH_SIZE = 2000


def seed():
    if not CSV_PATH.exists():
        print(f"[ERROR] CSV not found at {CSV_PATH}")
        sys.exit(1)

    init_db()
    db = SessionLocal()
    engine = RiskScoringEngine()

    try:
        # Skip if already seeded
        existing = db.query(Transaction).count()
        if existing > 0:
            print(f"[INFO] Database already contains {existing:,} transactions. Skipping seed.")
            return

        print(f"[INFO] Reading {CSV_PATH.name} ...")
        start = time.time()

        tx_batch: list[Transaction] = []
        alert_batch: list[dict] = []
        total = 0

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                raw = {
                    "step": int(row["step"]),
                    "transaction_type": row["type"],
                    "amount": float(row["amount"]),
                    "name_orig": row["nameOrig"],
                    "old_balance_orig": float(row["oldbalanceOrg"]),
                    "new_balance_orig": float(row["newbalanceOrig"]),
                    "name_dest": row["nameDest"],
                    "old_balance_dest": float(row["oldbalanceDest"]),
                    "new_balance_dest": float(row["newbalanceDest"]),
                    "is_fraud": row["isFraud"] == "1",
                    "is_flagged_fraud": row["isFlaggedFraud"] == "1",
                }

                score = engine.score(raw)
                raw.update(
                    risk_score=score["risk_score"],
                    severity=score["severity"],
                    fraud_detected=score["fraud_detected"],
                    risk_explanation=score["explanation"],
                )

                tx = Transaction(**raw)
                tx_batch.append(tx)
                total += 1

                # Flush batch
                if len(tx_batch) >= BATCH_SIZE:
                    db.bulk_save_objects(tx_batch)
                    db.flush()

                    # Collect alert seeds for fraud rows in this batch
                    for t in tx_batch:
                        if t.fraud_detected:
                            alert_batch.append(
                                dict(
                                    severity=t.severity,
                                    fraud_reason=t.risk_explanation or "Fraud detected",
                                    risk_score=t.risk_score or 0.0,
                                    status=AlertStatus.OPEN,
                                )
                            )

                    tx_batch.clear()

                    if total % 10000 == 0:
                        print(f"  Processed {total:,} rows ...")

        # Final partial batch
        if tx_batch:
            db.bulk_save_objects(tx_batch)
            db.flush()
            for t in tx_batch:
                if t.fraud_detected:
                    alert_batch.append(
                        dict(
                            severity=t.severity,
                            fraud_reason=t.risk_explanation or "Fraud detected",
                            risk_score=t.risk_score or 0.0,
                            status=AlertStatus.OPEN,
                        )
                    )
            tx_batch.clear()

        db.commit()
        print(f"[INFO] Committed {total:,} transactions.")

        # Now insert alerts (need real IDs from DB)
        print("[INFO] Creating fraud alerts ...")
        fraud_txs = (
            db.query(Transaction)
            .filter(Transaction.fraud_detected == True)  # noqa: E712
            .all()
        )
        alerts = [
            FraudAlert(
                transaction_id=tx.id,
                severity=tx.severity,
                fraud_reason=tx.risk_explanation or "Fraud detected",
                risk_score=tx.risk_score or 0.0,
                status=AlertStatus.OPEN,
            )
            for tx in fraud_txs
        ]
        db.bulk_save_objects(alerts)
        db.commit()

        elapsed = time.time() - start
        print(
            f"[DONE] Seeded {total:,} transactions and {len(alerts):,} alerts "
            f"in {elapsed:.1f}s"
        )

    except Exception as exc:
        db.rollback()
        print(f"[ERROR] Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
