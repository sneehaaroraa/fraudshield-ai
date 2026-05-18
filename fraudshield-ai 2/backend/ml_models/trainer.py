"""
backend/ml_models/trainer.py
──────────────────────────────
Trains a Random Forest fraud detection model on the PaySim dataset.

Usage (run once from project root):
    python -m backend.ml_models.trainer

Model is saved to:
    backend/ml_models/fraud_model.joblib
    backend/ml_models/model_meta.json
"""

from __future__ import annotations
import json
import zipfile
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, roc_auc_score, precision_score,
    recall_score, f1_score
)
import joblib

from backend.ml_models.preprocessor import preprocess_for_training

# Paths
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent.parent
CSV_ZIP = PROJECT_ROOT / "financial_transactions.csv.zip"
MODEL_PATH = BASE_DIR / "fraud_model.joblib"
META_PATH = BASE_DIR / "model_meta.json"

# Training config
SAMPLE_SIZE = 200_000   # rows to load (full file is ~6.3M)
TEST_SIZE = 0.2
RANDOM_STATE = 42


def load_dataset(sample_size: int = SAMPLE_SIZE) -> pd.DataFrame:
    """Load PaySim dataset from the bundled zip file."""
    if not CSV_ZIP.exists():
        raise FileNotFoundError(
            f"Dataset not found at {CSV_ZIP}. "
            "Place financial_transactions.csv.zip in the project root."
        )
    with zipfile.ZipFile(CSV_ZIP) as zf:
        csv_name = zf.namelist()[0]
        with zf.open(csv_name) as f:
            df = pd.read_csv(f, nrows=sample_size)
    print(f"Loaded {len(df):,} rows from dataset")
    return df


def train(sample_size: int = SAMPLE_SIZE) -> dict:
    """
    Full training pipeline:
    1. Load dataset
    2. Preprocess & engineer features
    3. Stratified train/test split
    4. Train RandomForest with class_weight='balanced' (handles imbalance)
    5. Evaluate on test set
    6. Save model + metadata
    """
    print("=== FraudShield ML Training Pipeline ===")

    # 1. Load
    df = load_dataset(sample_size)

    # 2. Preprocess
    X, y = preprocess_for_training(df)
    print(f"Features: {X.shape[1]} | Fraud rate: {y.mean():.4%}")

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    print(f"Train: {len(X_train):,} | Test: {len(X_test):,}")

    # 4. Train — balanced weights handle the class imbalance automatically
    print("Training RandomForest... (this takes ~30-60s)")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    metrics = {
        "auc_roc":   round(roc_auc_score(y_test, y_proba), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
        "accuracy":  round(report["accuracy"], 4),
    }
    print(f"Metrics: {metrics}")

    # Feature importance
    from backend.ml_models.preprocessor import get_feature_columns
    feature_names = get_feature_columns()
    importances = dict(zip(
        feature_names,
        [round(float(v), 4) for v in model.feature_importances_]
    ))

    # 6. Save
    joblib.dump(model, MODEL_PATH)
    meta = {
        "sample_size": sample_size,
        "n_features": X.shape[1],
        "feature_names": feature_names,
        "feature_importances": importances,
        "metrics": metrics,
        "trained_on_rows": len(X_train),
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Model saved → {MODEL_PATH}")
    print(f"Meta saved  → {META_PATH}")
    return meta


if __name__ == "__main__":
    train()
