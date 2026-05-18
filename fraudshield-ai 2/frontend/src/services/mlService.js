/**
 * src/services/mlService.js
 * ─────────────────────────
 * Frontend service for ML-powered analytics endpoints.
 *
 * Endpoints:
 *   GET /api/analytics/trends            — fraud trends over time
 *   GET /api/analytics/risk-distribution — risk histogram
 *   GET /api/analytics/type-risk         — per-type risk breakdown
 *   GET /api/analytics/model-info        — model training metadata
 *   POST /api/fraud/predict              — enhanced ML prediction
 */

import { apiClient } from './apiClient.js';

/** Fraud trends over time (grouped by step buckets) */
export async function getFraudTrends(buckets = 20) {
  const { data } = await apiClient.get('/analytics/trends', { params: { buckets } });
  return data;
}

/** Risk score distribution with fraud/legitimate split */
export async function getRiskDistribution() {
  const { data } = await apiClient.get('/analytics/risk-distribution');
  return data;
}

/** Per transaction-type risk and fraud breakdown */
export async function getTypeRisk() {
  const { data } = await apiClient.get('/analytics/type-risk');
  return data;
}

/** Trained model metadata and metrics */
export async function getModelInfo() {
  const { data } = await apiClient.get('/analytics/model-info');
  return data;
}

/**
 * Enhanced ML fraud prediction.
 * @param {Object} tx - transaction fields
 * @returns {Promise<{fraud_detected, risk_score, confidence_score, severity, explanation, ml_used}>}
 */
export async function mlPredict(tx) {
  const { data } = await apiClient.post('/fraud/predict', tx);
  return data;
}
