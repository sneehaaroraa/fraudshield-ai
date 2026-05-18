# ── FraudShield AI — Dockerfile ─────────────────────────────────────────────
# Builds the FastAPI backend for production deployment.
# Frontend is served as a static build (run: cd frontend && npm run build first).

from python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY data/ ./data/

# Copy trained ML model if present
COPY backend/ml_models/ ./backend/ml_models/

# Expose port
EXPOSE 8000

# Environment defaults (override via -e or .env)
ENV DATABASE_URL=sqlite:///./fraudshield.db
ENV AUTO_SEED=false

# Start server
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
