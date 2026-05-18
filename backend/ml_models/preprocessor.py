"""
backend/ml_models/preprocessor.py
──────────────────────────────────
PaySim dataset preprocessing for ML training and inference.

Handles:
- Column renaming (PaySim → internal names)
- Feature engineering
- Label encoding for transaction type
- Scaling numeric features
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Tuple


# PaySim CSV column name map → internal names
COLUMN_MAP = {
    "step":           "step",
    "type":           "transaction_type",
    "amount":         "amount",
    "nameOrig":       "name_orig",
    "oldbalanceOrg":  "old_balance_orig",
    "newbalanceOrig": "new_balance_orig",
    "nameDest":       "name_dest",
    "oldbalanceDest": "old_balance_dest",
    "newbalanceDest": "new_balance_dest",
    "isFraud":        "is_fraud",
    "isFlaggedFraud": "is_flagged_fraud",
}

TYPE_ENCODING = {
    "PAYMENT":  0,
    "TRANSFER": 1,
    "CASH_OUT": 2,
    "DEBIT":    3,
    "CASH_IN":  4,
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename PaySim CSV columns to internal names."""
    return df.rename(columns=COLUMN_MAP)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features that improve fraud detection:
    - balance_diff_orig: amount vs origin balance change
    - balance_diff_dest: amount vs destination balance change
    - orig_drained: origin account fully drained
    - dest_unchanged: destination balance unchanged after transfer
    - is_merchant_dest: destination is a merchant account (M-prefix)
    - type_encoded: numeric encoding of transaction type
    """
    df = df.copy()

    # Balance difference signals
    df["balance_diff_orig"] = df["old_balance_orig"] - df["new_balance_orig"]
    df["balance_diff_dest"] = df["new_balance_dest"] - df["old_balance_dest"]

    # Key fraud patterns from domain knowledge
    df["orig_drained"] = (
        (df["old_balance_orig"] > 0) &
        (df["new_balance_orig"] == 0)
    ).astype(int)

    df["dest_unchanged"] = (
        (df["amount"] > 0) &
        (abs(df["new_balance_dest"] - df["old_balance_dest"]) < 1.0) &
        (df["transaction_type"].isin(["TRANSFER", "CASH_OUT"]))
    ).astype(int)

    df["is_merchant_dest"] = df["name_dest"].str.startswith("M").astype(int)

    # Encode transaction type
    df["type_encoded"] = df["transaction_type"].map(TYPE_ENCODING).fillna(-1).astype(int)

    return df


def get_feature_columns() -> list[str]:
    """Return ordered list of feature columns used for training/inference."""
    return [
        "step",
        "type_encoded",
        "amount",
        "old_balance_orig",
        "new_balance_orig",
        "old_balance_dest",
        "new_balance_dest",
        "balance_diff_orig",
        "balance_diff_dest",
        "orig_drained",
        "dest_unchanged",
        "is_merchant_dest",
    ]


def preprocess_for_training(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Full preprocessing pipeline for training data.

    Returns:
        X: feature DataFrame
        y: fraud label Series
    """
    df = rename_columns(df)
    df = engineer_features(df)

    features = get_feature_columns()
    X = df[features].fillna(0)
    y = df["is_fraud"].astype(int)

    return X, y


def preprocess_single(tx: dict) -> pd.DataFrame:
    """
    Preprocess a single transaction dict for inference.
    Accepts both internal names and PaySim names.

    Returns a single-row DataFrame ready for model.predict().
    """
    # Normalize keys to internal names if needed
    normalized = {}
    reverse_map = {v: k for k, v in COLUMN_MAP.items()}
    for k, v in tx.items():
        internal_key = COLUMN_MAP.get(k, k)  # try PaySim name first
        normalized[internal_key] = v

    row = pd.DataFrame([normalized])
    row = engineer_features(row)

    features = get_feature_columns()
    # Fill any missing features with 0
    for col in features:
        if col not in row.columns:
            row[col] = 0

    return row[features].fillna(0)
