"""
transaction_service.py

Business logic for transaction retrieval.
All query-building lives here; routes stay thin.
"""

from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from  models.transaction_model import Transaction


# Columns that can be used for sorting (allowlist prevents SQL injection)
SORTABLE_COLUMNS = {
    "id": Transaction.id,
    "amount": Transaction.amount,
    "risk_score": Transaction.risk_score,
    "step": Transaction.step,
    "created_at": Transaction.created_at,
    "transaction_type": Transaction.transaction_type,
    "severity": Transaction.severity,
}


class TransactionService:
    """Handles all transaction read operations."""

    def get_transactions(
        self,
        db: Session,
        *,
        page: int = 1,
        page_size: int = 25,
        transaction_type: Optional[str] = None,
        fraud_only: bool = False,
        severity: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> dict:
        """
        Returns a paginated, filtered, sorted list of transactions.

        Returns:
            {
                "items": [...],
                "total": int,
                "page": int,
                "page_size": int,
                "total_pages": int,
            }
        """
        query = db.query(Transaction)

        # --- Filters ---
        if fraud_only:
            query = query.filter(Transaction.fraud_detected == True)  # noqa: E712

        if transaction_type:
            query = query.filter(
                Transaction.transaction_type == transaction_type.upper()
            )

        if severity:
            query = query.filter(
                Transaction.severity == severity.upper()
            )

        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)

        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.name_orig.ilike(pattern),
                    Transaction.name_dest.ilike(pattern),
                )
            )

        # --- Sorting ---
        sort_col = SORTABLE_COLUMNS.get(sort_by, Transaction.id)
        direction = desc if sort_order.lower() == "desc" else asc
        query = query.order_by(direction(sort_col))

        # --- Pagination ---
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        total_pages = max(1, (total + page_size - 1) // page_size)

        return {
            "items": [self._serialize(tx) for tx in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def get_transaction_by_id(self, db: Session, transaction_id: int) -> Optional[dict]:
        tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        return self._serialize(tx) if tx else None

    # ------------------------------------------------------------------
    # Serialiser
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize(tx: Transaction) -> dict:
        return {
            "id": tx.id,
            "step": tx.step,
            "transaction_type": tx.transaction_type,
            "amount": tx.amount,
            "name_orig": tx.name_orig,
            "old_balance_orig": tx.old_balance_orig,
            "new_balance_orig": tx.new_balance_orig,
            "name_dest": tx.name_dest,
            "old_balance_dest": tx.old_balance_dest,
            "new_balance_dest": tx.new_balance_dest,
            "is_fraud": tx.is_fraud,
            "is_flagged_fraud": tx.is_flagged_fraud,
            "risk_score": tx.risk_score,
            "severity": tx.severity,
            "fraud_detected": tx.fraud_detected,
            "risk_explanation": tx.risk_explanation,
            "created_at": tx.created_at.isoformat() if tx.created_at else None,
        }
