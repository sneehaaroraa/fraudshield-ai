"""
risk_scoring_engine.py

Rule-based fraud risk scoring engine for PaySim transactions.
Produces a 0–100 risk_score, a severity label, a fraud_detected flag,
and a human-readable explanation string.

Design decision: deterministic rules (no ML model) so scoring is
fully auditable, fast, and requires no training pipeline.

Severity thresholds:
    0–24   → LOW
    25–49  → MEDIUM
    50–74  → HIGH
    75–100 → CRITICAL
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuleResult:
    name: str
    triggered: bool
    score_delta: float
    reason: str


class RiskScoringEngine:
    """
    Evaluates a raw transaction dict and returns a risk assessment dict.

    Input keys (all required):
        transaction_type, amount, old_balance_orig, new_balance_orig,
        old_balance_dest, new_balance_dest, name_orig, name_dest,
        is_fraud, is_flagged_fraud

    Output dict keys:
        risk_score      float   0–100
        severity        str     LOW | MEDIUM | HIGH | CRITICAL
        fraud_detected  bool
        explanation     str
    """

    # Severity boundaries
    SEVERITY_BANDS = [
        (75, "CRITICAL"),
        (50, "HIGH"),
        (25, "MEDIUM"),
        (0,  "LOW"),
    ]

    # High-risk transaction types
    HIGH_RISK_TYPES = {"TRANSFER", "CASH_OUT"}

    def score(self, tx: dict[str, Any]) -> dict[str, Any]:
        rules = self._evaluate_rules(tx)
        triggered = [r for r in rules if r.triggered]

        raw_score = sum(r.score_delta for r in triggered)
        risk_score = min(100.0, max(0.0, raw_score))

        severity = self._classify_severity(risk_score)
        fraud_detected = risk_score >= 50 or tx.get("is_fraud", False)

        reasons = [r.reason for r in triggered] or ["No significant risk signals detected"]
        explanation = "; ".join(reasons)

        return {
            "risk_score": round(risk_score, 2),
            "severity": severity,
            "fraud_detected": fraud_detected,
            "explanation": explanation,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _evaluate_rules(self, tx: dict[str, Any]) -> list[RuleResult]:
        return [
            self._rule_ground_truth_fraud(tx),
            self._rule_flagged_fraud(tx),
            self._rule_high_risk_type(tx),
            self._rule_large_amount(tx),
            self._rule_origin_balance_drained(tx),
            self._rule_destination_balance_unchanged(tx),
            self._rule_zero_origin_balance_post(tx),
            self._rule_merchant_destination(tx),
            self._rule_round_amount(tx),
            self._rule_transfer_cash_out_combo(tx),
        ]

    # --- Individual rules -------------------------------------------

    @staticmethod
    def _rule_ground_truth_fraud(tx: dict) -> RuleResult:
        triggered = bool(tx.get("is_fraud", False))
        return RuleResult(
            name="ground_truth_fraud",
            triggered=triggered,
            score_delta=80.0 if triggered else 0.0,
            reason="Transaction labelled as fraud in dataset",
        )

    @staticmethod
    def _rule_flagged_fraud(tx: dict) -> RuleResult:
        triggered = bool(tx.get("is_flagged_fraud", False))
        return RuleResult(
            name="flagged_fraud",
            triggered=triggered,
            score_delta=20.0 if triggered else 0.0,
            reason="Transaction was system-flagged for fraud",
        )

    @classmethod
    def _rule_high_risk_type(cls, tx: dict) -> RuleResult:
        triggered = tx.get("transaction_type", "") in cls.HIGH_RISK_TYPES
        return RuleResult(
            name="high_risk_type",
            triggered=triggered,
            score_delta=15.0 if triggered else 0.0,
            reason=f"High-risk transaction type: {tx.get('transaction_type')}",
        )

    @staticmethod
    def _rule_large_amount(tx: dict) -> RuleResult:
        amount = float(tx.get("amount", 0))
        if amount >= 1_000_000:
            return RuleResult("large_amount", True, 25.0, f"Very large amount: {amount:,.2f}")
        if amount >= 200_000:
            return RuleResult("large_amount", True, 15.0, f"Large amount: {amount:,.2f}")
        if amount >= 50_000:
            return RuleResult("large_amount", True, 8.0, f"Moderately large amount: {amount:,.2f}")
        return RuleResult("large_amount", False, 0.0, "")

    @staticmethod
    def _rule_origin_balance_drained(tx: dict) -> RuleResult:
        old = float(tx.get("old_balance_orig", 0))
        new = float(tx.get("new_balance_orig", 0))
        amount = float(tx.get("amount", 0))
        triggered = old > 0 and new == 0 and amount >= old * 0.95
        return RuleResult(
            name="origin_balance_drained",
            triggered=triggered,
            score_delta=20.0 if triggered else 0.0,
            reason="Origin account fully drained by this transaction",
        )

    @staticmethod
    def _rule_destination_balance_unchanged(tx: dict) -> RuleResult:
        old = float(tx.get("old_balance_dest", 0))
        new = float(tx.get("new_balance_dest", 0))
        amount = float(tx.get("amount", 0))
        triggered = (
            amount > 0
            and abs(new - old) < 1.0
            and tx.get("transaction_type") in ("TRANSFER", "CASH_OUT")
        )
        return RuleResult(
            name="destination_balance_unchanged",
            triggered=triggered,
            score_delta=18.0 if triggered else 0.0,
            reason="Destination balance unchanged despite large transfer (possible layering)",
        )

    @staticmethod
    def _rule_zero_origin_balance_post(tx: dict) -> RuleResult:
        new = float(tx.get("new_balance_orig", -1))
        old = float(tx.get("old_balance_orig", -1))
        triggered = old > 0 and new == 0.0
        return RuleResult(
            name="zero_origin_balance_post",
            triggered=triggered,
            score_delta=10.0 if triggered else 0.0,
            reason="Origin account balance reduced to zero post-transaction",
        )

    @staticmethod
    def _rule_merchant_destination(tx: dict) -> RuleResult:
        dest = tx.get("name_dest", "")
        triggered = dest.startswith("M")
        return RuleResult(
            name="merchant_destination",
            triggered=triggered,
            score_delta=-5.0 if triggered else 0.0,   # merchants are lower risk
            reason="Destination is a merchant account (lower risk)",
        )

    @staticmethod
    def _rule_round_amount(tx: dict) -> RuleResult:
        amount = float(tx.get("amount", 0))
        triggered = amount > 1000 and amount % 1000 == 0
        return RuleResult(
            name="round_amount",
            triggered=triggered,
            score_delta=5.0 if triggered else 0.0,
            reason=f"Suspiciously round transaction amount: {amount:,.0f}",
        )

    @staticmethod
    def _rule_transfer_cash_out_combo(tx: dict) -> RuleResult:
        """
        Elevated risk when a TRANSFER or CASH_OUT fully drains the origin
        AND the destination is a non-merchant (C-prefix customer account).
        """
        tx_type = tx.get("transaction_type", "")
        dest = tx.get("name_dest", "")
        new_orig = float(tx.get("new_balance_orig", -1))
        old_orig = float(tx.get("old_balance_orig", 0))
        triggered = (
            tx_type in ("TRANSFER", "CASH_OUT")
            and dest.startswith("C")
            and old_orig > 0
            and new_orig == 0
        )
        return RuleResult(
            name="transfer_cash_out_combo",
            triggered=triggered,
            score_delta=15.0 if triggered else 0.0,
            reason="Transfer/CashOut fully drains origin to non-merchant customer",
        )

    def _classify_severity(self, score: float) -> str:
        for threshold, label in self.SEVERITY_BANDS:
            if score >= threshold:
                return label
        return "LOW"
