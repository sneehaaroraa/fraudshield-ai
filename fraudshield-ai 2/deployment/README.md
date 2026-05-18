# Deployment Guide — FraudShield AI

## Local Docker

```bash
# From project root:
cd frontend && npm run build      # builds to frontend/dist/
docker build -f deployment/Dockerfile -t fraudshield-ai .
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e AUTO_SEED=true \
  fraudshield-ai
```

## Railway (recommended free tier)

1. Push repo to GitHub
2. New project → Deploy from GitHub repo
3. Add environment variables from `.env.example`
4. Railway auto-detects Python and runs uvicorn

## Render

1. New Web Service → connect GitHub repo
2. Build command: `pip install -r backend/requirements.txt`
3. Start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
4. Add env vars from `.env.example`

## Environment Variables Required for Production

| Variable              | Description                         |
|-----------------------|-------------------------------------|
| `SECRET_KEY`          | Long random string for JWT signing  |
| `DATABASE_URL`        | PostgreSQL URL (or keep SQLite)     |
| `TOKEN_EXPIRE_MINUTES`| JWT lifetime (default 60)           |
| `FRONTEND_ORIGIN`     | Frontend URL for CORS               |
| `AUTO_SEED`           | Seed DB on startup (`true`/`false`) |
