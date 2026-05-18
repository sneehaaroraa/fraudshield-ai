/**
 * src/data/alerts.js
 * ────────────────────
 * Static incident timeline data for the AlertsTab.
 * This is a curated sample of SOC incident response events —
 * it is intentionally static (not from the DB) to show a realistic
 * timeline even during development or when alerts DB is empty.
 *
 * Phase 5+ goal: replace with live GET /api/fraud/alerts?limit=5&sort=recent
 */

export const INCIDENT_TIMELINE = [
  {
    id:        'INC-2024-001',
    timestamp: '2024-01-15T03:42:11Z',
    severity:  'CRITICAL',
    type:      'FULL_BALANCE_DRAIN',
    message:   'Account C00234891 drained — $847,200 TRANSFER to unverified merchant M01928374',
    mitre:     'T1070 — Full-Balance Drain',
    status:    'RESOLVED',
  },
  {
    id:        'INC-2024-002',
    timestamp: '2024-01-15T07:14:55Z',
    severity:  'HIGH',
    type:      'RAPID_SUCCESSION',
    message:   'Three consecutive CASH_OUT transactions within 4 minutes from C00198234',
    mitre:     'T1078 — Valid Accounts',
    status:    'INVESTIGATING',
  },
  {
    id:        'INC-2024-003',
    timestamp: '2024-01-15T11:30:02Z',
    severity:  'HIGH',
    type:      'LARGE_TRANSFER',
    message:   '$2.1M TRANSFER flagged — exceeds 10× account average monthly volume',
    mitre:     'T1041 — Exfiltration Over C2',
    status:    'ESCALATED',
  },
  {
    id:        'INC-2024-004',
    timestamp: '2024-01-15T14:08:33Z',
    severity:  'MEDIUM',
    type:      'ZERO_ORIGIN_ANOMALY',
    message:   'PAYMENT from zero-balance origin account C00445612 — $12,400',
    mitre:     'T1036 — Masquerading',
    status:    'OPEN',
  },
  {
    id:        'INC-2024-005',
    timestamp: '2024-01-15T18:55:49Z',
    severity:  'CRITICAL',
    type:      'FULL_BALANCE_DRAIN',
    message:   'Coordinated drain — 3 accounts emptied in 90-second window totalling $3.2M',
    mitre:     'T1070 — Full-Balance Drain',
    status:    'INVESTIGATING',
  },
  {
    id:        'INC-2024-006',
    timestamp: '2024-01-15T22:17:04Z',
    severity:  'LOW',
    type:      'UNUSUAL_HOUR',
    message:   'PAYMENT of $8,200 at 22:17 local — outside normal transaction window',
    mitre:     'T1078 — Valid Accounts',
    status:    'RESOLVED',
  },
];
