/**
 * src/services/api.js
 * ─────────────────────
 * Backward-compatible shim.
 * OverviewTab, MLTab and useTransactions already import from here.
 * We now delegate to fraudService so all calls go through one axios instance.
 *
 * Phase 4 change: routes updated from Express paths (/transactions)
 * to FastAPI paths (/fraud/transactions, /fraud/alerts, /fraud/predict).
 */

export { apiClient as api } from './apiClient.js';

import { getTransactions, getAlerts, updateAlert, predictTransaction } from './fraudService.js';
import { apiClient } from './apiClient.js';

// These exports keep existing hooks (useTransactions, MLTab, OverviewTab) working
// with zero modification to those files.
export { getTransactions, getAlerts, updateAlert };

export async function predictTransaction_compat(payload) {
  // MLTab sends slightly different field names — normalize them here
  return predictTransaction({
    type:        payload.type,
    amount:      payload.amount,
    oldBal:      payload.oldBal  ?? payload.old_balance_sender,
    newBal:      payload.newBal  ?? payload.new_balance_sender,
    oldBalDest:  payload.oldBalDest ?? payload.old_balance_receiver,
    newBalDest:  payload.newBalDest ?? payload.new_balance_receiver,
  });
}

// Keep old export name that MLTab uses
export { predictTransaction_compat as predictTransaction };

export async function getHealth() {
  const { data } = await apiClient.get('/health');
  return data;
}
