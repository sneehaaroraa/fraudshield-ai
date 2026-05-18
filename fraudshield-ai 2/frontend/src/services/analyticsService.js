/**
 * src/services/analyticsService.js
 * ───────────────────────────────────
 * Connects to GET /api/analytics/summary
 * Returns aggregated KPIs computed from the live SQLite database.
 */

import { apiClient } from './apiClient.js';

/**
 * Fetch analytics summary from backend.
 * Falls back to null if the backend isn't available yet.
 *
 * @returns {Promise<AnalyticsSummary | null>}
 *
 * AnalyticsSummary shape:
 * {
 *   total_transactions: number,
 *   total_fraud:        number,
 *   fraud_rate_pct:     number,
 *   total_flagged:      number,
 *   total_blocked:      number,
 *   total_cleared:      number,
 *   avg_risk_score:     number,
 *   open_alerts:        number,
 *   critical_alerts:    number,
 *   high_alerts:        number,
 *   by_type:            { type, count, fraud_count, fraud_rate }[],
 *   by_severity:        { severity, count }[],
 *   risk_bands:         { band, count }[],
 * }
 */
export async function getAnalyticsSummary() {
  const { data } = await apiClient.get('/analytics/summary');
  return data;
}
