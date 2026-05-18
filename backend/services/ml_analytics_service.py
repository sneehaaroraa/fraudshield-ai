"""
backend/services/ml_analytics_service.py
─────────────────────────────────────────
Provides ML-powered analytics endpoints:
  GET /analytics/trends          — fraud trends over time (by step/hour)
  GET /analytics/risk-distribution — risk score bucketing with fraud overlap
  GET /analytics/model-info      — trained model metadata + metrics
"""

from __future__ import annotations
from sqlalchemy import func, case, Float
from sqlalchemy.orm import Session
from  models.transaction_model import Transaction


class MLAnalyticsService:

    # ── Fraud Trends ─────────────────────────────────────────────────────────

    def get_fraud_trends(self, db: Session, buckets: int = 20) -> dict:
        """
        Aggregate transactions by step into time buckets.
        Returns fraud rate, total volume, and avg risk per bucket.

        buckets: number of time periods to group into (default 20)
        """
        # Get step range
        step_range = db.query(
            func.min(Transaction.step).label("min_step"),
            func.max(Transaction.step).label("max_step"),
        ).one()

        min_step = step_range.min_step or 1
        max_step = step_range.max_step or 1
        bucket_size = max(1, (max_step - min_step) // buckets)

        # Build bucket boundaries
        data = []
        for i in range(buckets):
            low = min_step + i * bucket_size
            high = low + bucket_size if i < buckets - 1 else max_step + 1

            row = db.query(
                func.count(Transaction.id).label("total"),
                func.sum(case((Transaction.is_fraud == True, 1), else_=0)).label("fraud_count"),
                func.round(func.avg(Transaction.risk_score), 1).label("avg_risk"),
                func.round(func.sum(Transaction.amount), 0).label("total_amount"),
            ).filter(
                Transaction.step >= low,
                Transaction.step < high,
            ).one()

            total = row.total or 0
            fraud = row.fraud_count or 0
            fraud_rate = round(fraud / total * 100, 4) if total else 0

            data.append({
                "period":       f"Step {low}–{high - 1}",
                "step_start":   low,
                "step_end":     high - 1,
                "total":        total,
                "fraud_count":  fraud,
                "fraud_rate":   fraud_rate,
                "avg_risk":     float(row.avg_risk or 0),
                "total_amount": float(row.total_amount or 0),
            })

        return {"buckets": buckets, "trends": data}

    # ── Risk Distribution ─────────────────────────────────────────────────────

    def get_risk_distribution(self, db: Session) -> dict:
        """
        Detailed risk score distribution with fraud overlap per band.
        Returns granular 10-point bands for histogram rendering.
        """
        bands = [
            ("0-9",   0,   10),
            ("10-19", 10,  20),
            ("20-29", 20,  30),
            ("30-39", 30,  40),
            ("40-49", 40,  50),
            ("50-59", 50,  60),
            ("60-69", 60,  70),
            ("70-79", 70,  80),
            ("80-89", 80,  90),
            ("90-100",90, 101),
        ]

        distribution = []
        for label, low, high in bands:
            row = db.query(
                func.count(Transaction.id).label("total"),
                func.sum(case((Transaction.is_fraud == True, 1), else_=0)).label("fraud_count"),
                func.round(func.avg(Transaction.amount), 2).label("avg_amount"),
            ).filter(
                Transaction.risk_score >= low,
                Transaction.risk_score < high,
            ).one()

            total = row.total or 0
            fraud = row.fraud_count or 0

            distribution.append({
                "band":          label,
                "range_low":     low,
                "range_high":    high - 1,
                "total":         total,
                "fraud_count":   fraud,
                "legitimate":    total - fraud,
                "fraud_rate":    round(fraud / total * 100, 2) if total else 0,
                "avg_amount":    float(row.avg_amount or 0),
            })

        # Summary stats
        overall = db.query(
            func.round(func.avg(Transaction.risk_score), 2).label("mean"),
            func.round(func.max(Transaction.risk_score), 2).label("max"),
            func.round(func.min(Transaction.risk_score), 2).label("min"),
        ).one()

        return {
            "distribution": distribution,
            "summary": {
                "mean_risk_score": float(overall.mean or 0),
                "max_risk_score":  float(overall.max or 0),
                "min_risk_score":  float(overall.min or 0),
            }
        }

    # ── Type-Level Risk Breakdown ─────────────────────────────────────────────

    def get_type_risk_breakdown(self, db: Session) -> list[dict]:
        """
        Per transaction-type breakdown of risk scores and fraud counts.
        Used to power the type-vs-risk analytics chart.
        """
        rows = db.query(
            Transaction.transaction_type.label("type"),
            func.count(Transaction.id).label("total"),
            func.sum(case((Transaction.is_fraud == True, 1), else_=0)).label("fraud_count"),
            func.round(func.avg(Transaction.risk_score), 1).label("avg_risk"),
            func.round(func.max(Transaction.risk_score), 1).label("max_risk"),
            func.round(func.sum(Transaction.amount), 0).label("total_volume"),
        ).group_by(Transaction.transaction_type).all()

        result = []
        for r in rows:
            total = r.total or 0
            fraud = r.fraud_count or 0
            result.append({
                "type":         r.type,
                "total":        total,
                "fraud_count":  fraud,
                "fraud_rate":   round(fraud / total * 100, 2) if total else 0,
                "avg_risk":     float(r.avg_risk or 0),
                "max_risk":     float(r.max_risk or 0),
                "total_volume": float(r.total_volume or 0),
            })

        # Sort by fraud rate descending
        return sorted(result, key=lambda x: x["fraud_rate"], reverse=True)
