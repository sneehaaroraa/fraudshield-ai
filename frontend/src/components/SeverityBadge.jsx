/**
 * src/components/SeverityBadge.jsx
 * ──────────────────────────────────
 * Reusable severity/status badge used across AlertsTab, TransactionsTab,
 * and AnalyticsTab. Keeps styling consistent without repeating logic.
 *
 * Usage:
 *   <SeverityBadge level="CRITICAL" />
 *   <SeverityBadge level="OPEN" type="status" />
 */

import { C, SEV_CLR } from '../theme/colors.js';

// Maps alert/transaction status → color
const STATUS_CLR = {
  OPEN:          C.red,
  INVESTIGATING: C.yellow,
  ESCALATED:     C.red,
  RESOLVED:      C.green,
  BLOCKED:       C.red,
  FLAGGED:       C.yellow,
  CLEAR:         C.green,
};

export function SeverityBadge({ level = 'LOW', type = 'severity', small = false }) {
  const color = type === 'severity'
    ? (SEV_CLR[level] || C.muted)
    : (STATUS_CLR[level] || C.muted);

  return (
    <span
      style={{
        display:       'inline-flex',
        alignItems:    'center',
        gap:           4,
        padding:       small ? '2px 7px' : '3px 9px',
        borderRadius:  3,
        border:        `1px solid ${color}44`,
        background:    `${color}18`,
        color,
        fontSize:      small ? 9 : 10,
        fontFamily:    'Space Mono',
        letterSpacing: 0.5,
        fontWeight:    600,
        whiteSpace:    'nowrap',
      }}
    >
      {/* Dot indicator */}
      <span
        style={{
          width:        5,
          height:       5,
          borderRadius: '50%',
          background:   color,
          flexShrink:   0,
        }}
      />
      {level}
    </span>
  );
}

/**
 * Compact inline risk score chip — shows the numeric score colored by band.
 * Usage: <RiskChip score={85} />
 */
export function RiskChip({ score }) {
  const n     = Number(score) || 0;
  const color = n >= 85 ? C.red : n >= 70 ? C.yellow : n >= 55 ? C.accent : C.green;
  return (
    <span
      style={{
        fontFamily:    'Space Mono',
        fontSize:      11,
        fontWeight:    700,
        color,
        background:    `${color}18`,
        border:        `1px solid ${color}33`,
        borderRadius:  3,
        padding:       '1px 7px',
      }}
    >
      {n}
    </span>
  );
}
