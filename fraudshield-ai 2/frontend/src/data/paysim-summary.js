/**
 * src/data/paysim-summary.js
 * ───────────────────────────
 * Static summary of the PaySim dataset used as chart fallback when
 * the live backend is unavailable or still loading.
 *
 * Source: Kaggle PaySim (6.3M transactions, 30-day simulation)
 * These numbers are pre-aggregated from the full dataset.
 */

export const PAYSIM = {
  // ── Overview KPIs ─────────────────────────────────────────────────────────
  overview: {
    total_transactions: 6362620,
    total_fraud:        8213,
    fraud_rate:         0.129,      // %
    total_amount:       91812.4,    // in millions
    avg_risk_score:     22.4,
  },

  // ── Fraud by Transaction Type ─────────────────────────────────────────────
  fraud_by_type: [
    { type: 'TRANSFER',  fraud: 4097, total: 532909,  fraud_rate: 0.77 },
    { type: 'CASH_OUT',  fraud: 4116, total: 2237500, fraud_rate: 0.18 },
    { type: 'PAYMENT',   fraud: 0,    total: 2151495, fraud_rate: 0.00 },
    { type: 'CASH_IN',   fraud: 0,    total: 1399284, fraud_rate: 0.00 },
    { type: 'DEBIT',     fraud: 0,    total: 41432,   fraud_rate: 0.00 },
  ],

  // ── Severity Distribution (rule-based estimates) ──────────────────────────
  severity_distribution: [
    { severity: 'CRITICAL', count: 1240,  pct: 15.1 },
    { severity: 'HIGH',     count: 2880,  pct: 35.1 },
    { severity: 'MEDIUM',   count: 2450,  pct: 29.8 },
    { severity: 'LOW',      count: 1643,  pct: 20.0 },
  ],

  // ── Amount statistics by type (millions) ─────────────────────────────────
  amount_by_type: [
    { type: 'TRANSFER',  avg: 1.79, max: 10,   total: 954.1 },
    { type: 'CASH_OUT',  avg: 1.79, max: 10,   total: 4003.2 },
    { type: 'PAYMENT',   avg: 0.18, max: 20,   total: 387.2 },
    { type: 'CASH_IN',   avg: 1.36, max: 10,   total: 1900.7 },
    { type: 'DEBIT',     avg: 0.64, max: 10,   total: 26.5 },
  ],

  // ── Fraud over time (sampled time buckets, 30 steps) ─────────────────────
  fraud_over_time: [
    { step: 1,   fraud: 0,   total: 5156 },
    { step: 50,  fraud: 96,  total: 16124 },
    { step: 100, fraud: 178, total: 21408 },
    { step: 150, fraud: 320, total: 23872 },
    { step: 200, fraud: 612, total: 26540 },
    { step: 250, fraud: 984, total: 25408 },
    { step: 300, fraud: 1342,total: 24116 },
    { step: 350, fraud: 1196,total: 22048 },
    { step: 400, fraud: 987, total: 19876 },
    { step: 450, fraud: 654, total: 18432 },
    { step: 500, fraud: 412, total: 14320 },
    { step: 550, fraud: 198, total: 10560 },
    { step: 600, fraud: 96,  total: 7240  },
    { step: 650, fraud: 42,  total: 4128  },
    { step: 700, fraud: 18,  total: 2016  },
    { step: 744, fraud: 4,   total: 820   },
  ],
};
