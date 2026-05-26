"""
backend/services/fraud_prediction_service.py
─────────────────────────────────────────────
Singleton service that wraps the trained RandomForest model.

- Loads model from disk once at startup
- Falls back to rule-based scoring if model is not trained yet
- Returns standardized prediction response with explanation

Prediction response schema:
    fraud_detected  bool
    risk_score      float  (0-100)
    confidence_score float (0-1, model probability)
    severity        str    LOW | MEDIUM | HIGH | CRITICAL
    explanation     str    human-readable reason
    ml_used         bool   whether ML model was used
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from ..ml_models.preprocessor import preprocess_single, get_feature_columns
from ..fraud_engine.risk_scoring_engine import RiskScoringEngine

BASE_DIR = Path(__file__).parent.parent / "ml_models"
MODEL_PATH = BASE_DIR / "fraud_model.joblib"
META_PATH = BASE_DIR / "model_meta.json"

SEVERITY_BANDS = [
    (75, "CRITICAL"),
    (50, "HIGH"),
    (25, "MEDIUM"),
    (0,  "LOW"),
]


def _classify_severity(score: float) -> str:
    for threshold, label in SEVERITY_BANDS:
        if score >= threshold:
            return label
    return "LOW"


class FraudPredictionService:
    """
    Singleton ML prediction service.
    Call predict(tx_dict) to get a standardized fraud assessment.
    """

    _instance: "FraudPredictionService | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = None
            cls._instance._meta = None
            cls._instance._rule_engine = RiskScoringEngine()
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Load persisted model from disk if available."""
        if MODEL_PATH.exists():
            try:
                self._model = joblib.load(MODEL_PATH)
                if META_PATH.exists():
                    with open(META_PATH) as f:
                        self._meta = json.load(f)
                print("[FraudPredictionService] ML model loaded ✓")
            except Exception as e:
                print(f"[FraudPredictionService] Failed to load model: {e}")
                self._model = None
        else:
            print("[FraudPredictionService] No trained model found — using rule-based fallback")

    def reload_model(self):
        """Reload model from disk (call after training)."""
        self._model = None
        self._meta = None
        self._load_model()

    @property
    def model_ready(self) -> bool:
        return self._model is not None

    def predict(self, tx: dict[str, Any]) -> dict[str, Any]:
        """
        Predict fraud risk for a single transaction.

        Args:
            tx: transaction dict with PaySim or internal field names

        Returns:
            {
                fraud_detected, risk_score, confidence_score,
                severity, explanation, ml_used
            }
        """
        if self._model is not None:
            return self._ml_predict(tx)
        else:
            return self._rule_predict(tx)

    def _ml_predict(self, tx: dict) -> dict:
        """Use RandomForest model for prediction."""
        X = preprocess_single(tx)

        proba = self._model.predict_proba(X)[0]
        fraud_prob = float(proba[1])

        # Scale probability to 0-100 risk score with amplification
        # Raw fraud_prob for fraud transactions is ~0.5-0.9
        risk_score = min(100.0, fraud_prob * 130)

        # Also run rule engine for explainability
        rule_result = self._rule_engine.score(tx)

        # Blend: 70% ML + 30% rules (rules provide signal for edge cases)
        blended_score = 0.7 * risk_score + 0.3 * rule_result["risk_score"]
        blended_score = round(min(100.0, blended_score), 2)

        fraud_detected = blended_score >= 50 or fraud_prob >= 0.5

        severity = _classify_severity(blended_score)

        # Build explanation using feature importances
        explanation = self._build_explanation(tx, fraud_prob, rule_result)

        return {
            "fraud_detected":   fraud_detected,
            "risk_score":       blended_score,
            "confidence_score": round(fraud_prob, 4),
            "severity":         severity,
            "explanation":      explanation,
            "ml_used":          True,
        }

    def _rule_predict(self, tx: dict) -> dict:
        """Fallback: pure rule-based scoring when model isn't trained."""
        result = self._rule_engine.score(tx)
        risk_score = result["risk_score"]
        return {
            "fraud_detected":   result["fraud_detected"],
            "risk_score":       risk_score,
            "confidence_score": round(risk_score / 100, 4),
            "severity":         result["severity"],
            "explanation":      result["explanation"] + " [rule-based fallback — run trainer.py to enable ML]",
            "ml_used":          False,
        }

    def _build_explanation(self, tx: dict, fraud_prob: float, rule_result: dict) -> str:
        """Build a human-readable explanation combining ML signal + rules."""
        parts = []

        prob_pct = round(fraud_prob * 100, 1)
        parts.append(f"ML model assigns {prob_pct}% fraud probability")

        # Highlight key rule signals
        rule_explanation = rule_result.get("explanation", "")
        if rule_explanation and "No significant" not in rule_explanation:
            # Trim to top 2 rules
            rule_parts = rule_explanation.split("; ")[:2]
            parts.extend(rule_parts)

        # Add transaction-level context
        tx_type = tx.get("transaction_type") or tx.get("type", "")
        amount = tx.get("amount", 0)
        if tx_type in ("TRANSFER", "CASH_OUT") and amount > 100_000:
            parts.append(f"High-value {tx_type} of {amount:,.0f}")

        return "; ".join(parts)

    def get_model_info(self) -> dict:
        """Return model metadata for API /analytics/model-info."""
        if not self._meta:
            return {"status": "not_trained", "message": "Run python -m backend.ml_models.trainer to train the model"}
        return {
            "status": "ready",
            **self._meta,
        }


# Module-level singleton
fraud_predictor = FraudPredictionService()
