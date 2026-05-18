/**
 * src/components/State.jsx
 * ─────────────────────────
 * Shared loading and error state components used across all tabs.
 *
 * Components:
 *   LoadingState — centered spinner with optional label
 *   ErrorState   — error message with icon
 *   EmptyState   — placeholder for empty data
 */

import { C } from '../theme/colors.js';
import { Spinner } from './atoms.jsx';

// ── LoadingState ──────────────────────────────────────────────────────────────
export function LoadingState({ label = 'Loading...' }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 12,
      padding: '48px 24px',
      color: C.muted,
      fontFamily: 'Space Mono, monospace',
      fontSize: 11,
      letterSpacing: 1,
    }}>
      <Spinner size={28} color={C.accent} />
      <span>{label.toUpperCase()}</span>
    </div>
  );
}

// ── ErrorState ────────────────────────────────────────────────────────────────
export function ErrorState({ message = 'An error occurred.' }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      padding: '14px 16px',
      borderRadius: 8,
      background: `rgba(239,68,68,0.08)`,
      border: `1px solid rgba(239,68,68,0.25)`,
      color: C.red,
      fontFamily: 'Space Mono, monospace',
      fontSize: 11,
      margin: '12px 0',
    }}>
      <span style={{ fontSize: 16 }}>⚠</span>
      <span>{message}</span>
    </div>
  );
}

// ── EmptyState ────────────────────────────────────────────────────────────────
export function EmptyState({ icon = '📭', label = 'No data found.', sublabel = '' }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 8,
      padding: '48px 24px',
      color: C.muted,
      textAlign: 'center',
    }}>
      <span style={{ fontSize: 32 }}>{icon}</span>
      <div style={{ fontSize: 13, color: C.muted }}>{label}</div>
      {sublabel && <div style={{ fontSize: 11, color: C.dim }}>{sublabel}</div>}
    </div>
  );
}
