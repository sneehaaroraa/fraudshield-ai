# 🛡️ FraudShield AI
### Financial Fraud Detection & Cybersecurity Threat Response Platform

> Production-style SOC platform powered by 6.3M PaySim transactions, FastAPI, React + Vite.

---

## Architecture

```
financial-fraud-cybersecurity/
├── frontend/          # React + Vite (SOC dashboard UI)
├── backend/           # FastAPI + SQLAlchemy
│   ├── app.py         # entry point
│   ├── routes/        # HTTP endpoints
│   ├── fraud_engine/  # rule-based scorer (ML-ready)
│   ├── services/      # data loading & seeding
│   ├── models/        # SQLAlchemy ORM tables
│   ├── database/      # engine + session
│   └── auth/          # JWT utilities (Phase 2)
├── data/              # transactions.json (5 000-row sample)
├── analytics/         # notebooks & reports
├── ml_models/         # trained model files (.joblib)
├── compliance/        # GDPR / PCI-DSS mapping docs
└── screenshots/       # dashboard screenshots
```

---

## Tech Stack

| Layer      | Technology                    |
|------------|-------------------------------|
| Frontend   | React 18, Vite, Recharts      |
| Backend    | FastAPI, Uvicorn              |
| Database   | SQLite (dev) → Postgres (prod)|
| ORM        | SQLAlchemy 2.0                |
| Auth       | JWT (python-jose) + bcrypt    |
| ML         | scikit-learn, joblib, pandas  |
| Dataset    | PaySim (6.36M transactions)   |

---

## Quick Start

### 1. Backend
```bash
cd financial-fraud-cybersecurity
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # fill in SECRET_KEY

uvicorn backend.app:app --reload --port 8000
```

API docs auto-generated at: **http://localhost:8000/docs**

### 2. Frontend
```bash
cd frontend
npm install
npm run dev                        # proxies /api → :8000
```

---

## API Endpoints

| Method | Endpoint                     | Description                        |
|--------|------------------------------|------------------------------------|
| GET    | `/api/health`                | Server health check                |
| GET    | `/api/fraud/transactions`    | Paginated, filterable transactions |
| POST   | `/api/fraud/predict`         | Score a transaction on-the-fly     |
| GET    | `/api/fraud/alerts`          | SIEM alert feed                    |
| GET    | `/api/fraud/alerts/{id}`     | Single alert detail                |
| PATCH  | `/api/fraud/alerts/{id}`     | Update alert status / notes        |

### Query parameters — `/api/fraud/transactions`
| Param      | Type    | Default | Description                    |
|------------|---------|---------|--------------------------------|
| search     | string  | ""      | Filter by tx_id / orig / dest  |
| type       | string  | "ALL"   | TRANSFER, CASH_OUT, PAYMENT …  |
| status     | string  | "ALL"   | CLEAR, FLAGGED, BLOCKED        |
| fraudOnly  | bool    | false   | Show only flagged fraud         |
| page       | int     | 1       | Page number                    |
| pageSize   | int     | 12      | Rows per page (max 50)         |

---

## Dataset

PaySim synthetic financial transactions — **6,362,620 rows**.
- `data/transactions.json` — 5,000-row backend sample (1,000 fraud + 4,000 legit)
- Full CSV required for ML training (not committed to git)

---

## Fraud Scoring Rules

| Rule    | Condition                        | Points |
|---------|----------------------------------|--------|
| PAY-001 | TRANSFER or CASH_OUT type        | +20    |
| PAY-002 | Amount > $100,000                | +18    |
| PAY-003 | Amount > $1,000,000              | +18    |
| PAY-004 | Full-balance drain               | +34    |
| PAY-005 | Zero-origin-balance anomaly      | +8     |

Threshold: **≥ 55 = FRAUD**, **≥ 85 = CRITICAL**

---

## Roadmap

- [x] Phase 1 — Backend foundation + API
- [ ] Phase 2 — JWT authentication + role-based access
- [ ] Phase 3 — ML model (RandomForest on full PaySim)
- [ ] Phase 4 — WebSocket live feed
- [ ] Phase 5 — Deployment (Render backend + Vercel frontend)
