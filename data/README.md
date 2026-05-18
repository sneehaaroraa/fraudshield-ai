# Data

## financial_transactions.csv.zip

**Source:** [PaySim — Synthetic Financial Transactions Dataset](https://www.kaggle.com/datasets/ealaxi/paysim1)

**Size:** ~470 MB uncompressed (~6.3 million transactions)

**Columns:**

| Column          | Description                                       |
|-----------------|---------------------------------------------------|
| `step`          | Time step (1 step = 1 hour, max 744 = 30 days)   |
| `type`          | PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN       |
| `amount`        | Transaction amount in local currency              |
| `nameOrig`      | Customer initiating transaction                   |
| `oldbalanceOrg` | Balance before transaction (sender)               |
| `newbalanceOrig`| Balance after transaction (sender)                |
| `nameDest`      | Recipient                                         |
| `oldbalanceDest`| Recipient balance before transaction              |
| `newbalanceDest`| Recipient balance after transaction               |
| `isFraud`       | Ground truth label (1 = fraud)                    |
| `isFlaggedFraud`| Flagged by PaySim's internal rules                |

**Usage:**

```bash
# Train the ML model using this dataset:
python -m backend.ml_models.trainer

# Or seed the SQLite database with a sample:
AUTO_SEED=true uvicorn backend.app:app --reload
```
