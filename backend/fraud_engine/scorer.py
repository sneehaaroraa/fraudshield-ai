"""
backend/fraud_engine/scorer.py
───────────────────────────────
Rule-based fraud scorer.

Why keep rules separate from routes?
  - Easy to swap with an ML model later (Phase 3)
  - Unit-testable in isolation
  - Keeps route handlers thin and readable

Scoring rules (additive, capped 0-99):
  PAY-001  TRANSFER or CASH_OUT type              +20
  PAY-002  Amount > $100,000                      +18
  PAY-003  Amount > $1,000,000                    +18 (stacks with PAY-002)
  PAY-004  Full-balance drain (oldBal ≈ amount,   +34
           newBal = 0) — classic account-takeover
  PAY-005  Zero-origin-balance anomaly             +8
  BASE     Every transaction starts at 8
"""

from __future__ import annotations


# MITRE ATT&CK techniques matched to rule patterns
MITRE_MAP: dict[str, str] = {
    "PAY-001": "T1078 Valid Accounts",
    "PAY-002": "T1041 Exfiltration Over C2",
    "PAY-003": "T1083 Large Value Movement",
    "PAY-004": "T1070 Full-Balance Drain",
    "PAY-005": "T1036 Zero-Origin Anomaly",
}


def score(tx: dict) -> dict:
    """
    Score a single transaction dict.

    Args:
        tx: dict with keys: amount, oldBal, newBal, type

    Returns:
        dict with: prediction, risk_score, severity, probability, rules, mitre
    """
    amount  = float(tx.get("amount",  tx.get("oldBal", 0)) or 0)
    old_bal = float(tx.get("oldBal",  tx.get("old_bal", 0)) or 0)
    new_bal = float(tx.get("newBal",  tx.get("new_bal", 0)) or 0)
    tx_type = str(tx.get("type", "")).upper()

    points = 8   # base score
    rules: list[str] = []

    if tx_type in ("TRANSFER", "CASH_OUT"):
        points += 20
        rules.append("PAY-001")

    if amount > 100_000:
        points += 18
        rules.append("PAY-002")

    if amount > 1_000_000:
        points += 18
        rules.append("PAY-003")

    # Full-balance drain: sender emptied the account exactly
    if old_bal > 0 and abs(old_bal - amount) < 1 and new_bal == 0:
        points += 34
        rules.append("PAY-004")

    if old_bal == 0 and amount > 0:
        points += 8
        rules.append("PAY-005")

    risk_score = max(0, min(99, round(points)))
    is_fraud   = risk_score >= 55

    severity = (
        "CRITICAL" if risk_score >= 85 else
        "HIGH"     if risk_score >= 70 else
        "MEDIUM"   if risk_score >= 55 else
        "LOW"
    )

    mitre_hits = [MITRE_MAP[r] for r in rules if r in MITRE_MAP]

    return {
        "prediction":  "FRAUD" if is_fraud else "LEGITIMATE",
        "risk_score":  risk_score,
        "probability": round(risk_score / 100, 4),
        "severity":    severity,
        "rules":       rules,
        "mitre":       mitre_hits,
        "status":      "BLOCKED" if risk_score >= 85 else "FLAGGED" if is_fraud else "CLEAR",
    }
