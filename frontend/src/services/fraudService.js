/**
 * src/services/fraudService.js
 * ──────────────────────────────
 * All fraud-related API calls.
 * Routes mirror the FastAPI backend exactly:
 *   GET  /api/fraud/transactions
 *   GET  /api/fraud/alerts
 *   GET  /api/fraud/alerts/:id
 *   PATCH /api/fraud/alerts/:id
 *   POST /api/fraud/predict
 */

import { apiClient } from './apiClient.js';

// ── Transactions ───────────────────────────────────────────────────────────

/**
 * Fetch paginated, filterable transactions.
 * @param {object} params - { search, type, status, fraudOnly, page, pageSize }
 * @returns { data: Transaction[], pagination: {...} }
 */
export async function getTransactions(params = {}) {
  const { data } = await apiClient.get('/fraud/transactions', { params });
  return data;
}

// ── Alerts ─────────────────────────────────────────────────────────────────

/**
 * Fetch SIEM alerts with optional severity/status filters.
 * @param {object} params - { severity, status, page, pageSize }
 * @returns { data: Alert[], pagination: {...} }
 */
export async function getAlerts(params = {}) {
  const { data } = await apiClient.get('/fraud/alerts', { params });
  return data;
}

/**
 * Fetch a single alert by ID.
 * @param {string} alertId - e.g. "ALT-0001"
 */
export async function getAlert(alertId) {
  const { data } = await apiClient.get(`/fraud/alerts/${alertId}`);
  return data;
}

/**
 * Update alert status or analyst notes.
 * @param {string} alertId
 * @param {{ status?: string, notes?: string }} patch
 */
export async function updateAlert(alertId, patch) {
  const { data } = await apiClient.patch(`/fraud/alerts/${alertId}`, patch);
  return data;
}

// ── Risk prediction ────────────────────────────────────────────────────────

/**
 * Score a single transaction through the fraud engine.
 * @param {{ type, amount, oldBal, newBal, isFraud? }} tx
 * @returns { prediction, risk_score, severity, rules, mitre, explanation }
 */
export async function predictTransaction(tx) {
  const { data } = await apiClient.post('/fraud/predict', tx);
  return data;
}
