# 🛡️ FraudShield AI

> **Financial Fraud Detection & Cybersecurity Threat Response Platform**
> Full-stack AI-powered SIEM dashboard — FastAPI · React · RandomForest ML

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?logo=scikit-learn)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Project Overview

FraudShield AI is a production-grade **Security Operations Center (SOC) dashboard** that detects financial fraud in real time. It combines a **RandomForest ML model** (trained on 6M+ PaySim transactions, AUC-ROC ~0.98) with a deterministic **MITRE ATT&CK rule engine** for robust fallback coverage.

Built as a portfolio project demonstrating full-stack engineering, machine learning in production, and cybersecurity domain knowledge.

---

## ✅ Features

### 🤖 ML Fraud Detection
- RandomForest classifier trained on PaySim dataset (6M+ synthetic financial transactions)
- 70/30 ML + rule-based blending for robustness
- Automatic fallback to rule engine when model is unavailable
- MITRE ATT&CK technique tagging on every alert

### 📊 Live Dashboard
- Paginated transaction table with filtering, search, and sort
- Real-time KPI cards: total transactions, fraud rate, flagged amount, active alerts
- Fraud-by-type bar charts, severity distribution, risk score histograms

### 🚨 Alert Management
- Full OPEN → INVESTIGATING → ESCALATED → RESOLVED workflow
- Severity tagging (CRITICAL / HIGH / MEDIUM / LOW)
- MITRE ATT&CK technique IDs linked to each alert

### 📈 Analytics & ML Insights
- Fraud trends over time
- Risk-score distribution histograms
- Per-transaction-type risk breakdown
- Live model metadata (accuracy, last trained, feature count)

### 🔐 Authentication
- JWT-based login / register / `/me`
- Role-based access: `admin`, `analyst`, `auditor`
- Persistent sessions via localStorage with auto-renewal

---

## 🏗️ Architecture

```
fraudshield-ai/
├── frontend/                    # React 18 + Vite + Tailwind + Recharts
│   └── src/
│       ├── pages/               # Landing, Login
│       ├── layout/              # Dashboard shell (sidebar, tabs)
│       ├── components/          # AlertsTab, AnalyticsTab, MLInsightsTab, atoms
│       ├── hooks/               # useAlerts, useAnalytics
│       ├── services/            # apiClient, authApi, fraudService, mlService
│       ├── auth/                # useAuth hook (JWT session management)
│       └── theme/               # colors.js, StyleInject
├── backend/                     # FastAPI + SQLAlchemy + SQLite
│   ├── app.py                   # Entry point, CORS, router registration
│   ├── routes/                  # auth_router, fraud_routes, analytics_routes, ml_routes
│   ├── models/                  # SQLAlchemy: User, Transaction, FraudAlert
│   ├── services/                # Business logic: transaction, alert, analytics, ML
│   ├── fraud_engine/            # Rule scorer + MITRE ATT&CK risk engine
│   ├── ml_models/               # preprocessor, trainer, fraud_model.joblib
│   ├── auth/                    # JWT handler (python-jose + bcrypt)
│   └── database/                # db engine, seed data
├── data/
│   └── financial_transactions.csv.zip   # PaySim dataset
├── deployment/                  # Dockerfile
├── screenshots/                 # Portfolio screenshots
├── vercel.json                  # Frontend deployment (Vercel)
├── render.yaml                  # Backend deployment (Render)
└── .env.example
```

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Recharts, Axios |
| Backend | FastAPI, SQLAlchemy, SQLite / PostgreSQL |
| ML Engine | scikit-learn (RandomForest), pandas, joblib |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Deployment | Vercel (frontend) + Render (backend) |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone & configure

```bash
git clone https://github.com/yourusername/fraudshield-ai.git
cd fraudshield-ai
cp .env.example .env          # edit SECRET_KEY and other values
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start with demo data:
AUTO_SEED=true uvicorn backend.app:app --reload --port 8000
```

API docs available at: **https://fraudshield-bwfm.onrender.com/docs**

### 3. Train the ML model (optional)

The pre-trained model (`fraud_model.joblib`) is included. To retrain:

```bash
cd data && unzip financial_transactions.csv.zip
python -m backend.ml_models.trainer
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev       # → http://localhost:5173
```

### 5. Demo login

Register an account, or use the seeded credentials:
- **Email:** `admin@fraudshield.ai`
- **Password:** `Admin1234!`

---

## 🤖 ML Model Performance

Trained on the PaySim synthetic financial transactions dataset (6.3M transactions):

| Metric | Score |
|--------|-------|
| AUC-ROC | ~0.98 |
| Precision | ~0.95 |
| Recall | ~0.90 |
| F1 Score | ~0.92 |

The system blends ML predictions (70%) with rule-based scoring (30%). If the model file is absent, it falls back entirely to the deterministic rule engine.

---

## 🔐 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | ❌ | Create account, returns JWT |
| `POST` | `/api/auth/login` | ❌ | Login, returns JWT |
| `GET` | `/api/auth/me` | ✅ | Current user profile |
| `GET` | `/api/fraud/transactions` | ✅ | Paginated transaction list |
| `GET` | `/api/fraud/alerts` | ✅ | Paginated alert list |
| `PATCH` | `/api/fraud/alerts/{id}/status` | ✅ | Update alert status |
| `POST` | `/api/fraud/predict` | ✅ | Score an ad-hoc transaction |
| `GET` | `/api/analytics/summary` | ✅ | Dashboard KPIs |
| `GET` | `/api/analytics/trends` | ✅ | Fraud trends over time |
| `GET` | `/api/analytics/risk-distribution` | ✅ | Risk score histogram |
| `GET` | `/api/analytics/type-risk` | ✅ | Risk by transaction type |
| `GET` | `/api/analytics/model-info` | ✅ | ML model metadata |
| `GET` | `/api/health` | ❌ | Liveness probe |

Interactive Swagger UI: `https://fraudshield-bwfm.onrender.com/docs`

---

## 🐳 Docker

```bash
docker build -f deployment/Dockerfile -t fraudshield-ai .
docker run -p 8000:8000 -e AUTO_SEED=true fraudshield-ai
```

---

## ☁️ Deployment

### Frontend → Vercel

```bash
cd frontend && npm run build
# Push to GitHub → import at vercel.com
# Set env var: VITE_API_BASE_URL=https://your-backend.onrender.com/api
```

### Backend → Render

1. Push repo to GitHub
2. New Web Service on [render.com](https://render.com)
3. Build: `pip install -r backend/requirements.txt`
4. Start: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
5. Add env vars from `.env.example`
6. Set `FRONTEND_ORIGIN` to your Vercel URL

Or use the included `render.yaml` for streamlined setup.

---

## 🔮 Future Improvements

- [ ] PostgreSQL for production (env switch already wired)
- [ ] WebSocket real-time alert streaming
- [ ] TOTP two-factor authentication
- [ ] Export transactions to CSV / PDF
- [ ] Email notifications for CRITICAL alerts
- [ ] Graph-based anomaly detection (transaction network analysis)

---

## 📄 License

MIT — free to use, fork, and build on.
