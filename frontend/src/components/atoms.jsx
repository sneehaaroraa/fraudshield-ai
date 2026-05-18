/**
 * src/components/atoms.jsx
 * ─────────────────────────
 * Tiny, stateless UI primitives shared across the dashboard.
 *
 * Components:
 *   Badge      — colored pill label (status, type, count)
 *   LivePill   — animated "LIVE" indicator dot
 *   ThreatDot  — small colored dot for severity/threat indicators
 *   Spinner    — loading spinner
 *   Divider    — horizontal separator
 */

import { C } from '../theme/colors.js';

// ── Badge ─────────────────────────────────────────────────────────────────────
/**
 * Colored pill label.
 * @param {string}  color — text color
 * @param {string}  bg    — background color
 * @param {string}  children
 */
export function Badge({ color = C.accent, bg = C.accentDim, children, style = {} }) {
  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 8px',
      borderRadius: 4,
      fontSize: 10,
      fontFamily: 'Space Mono, monospace',
      fontWeight: 700,
      letterSpacing: 0.5,
      color,
      background: bg,
      whiteSpace: 'nowrap',
      ...style,
    }}>
      {children}
    </span>
  );
}

// ── LivePill ──────────────────────────────────────────────────────────────────
/**
 * Animated "● LIVE" indicator — shows real-time data feed status.
 */
export function LivePill() {
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 5,
      padding: '3px 8px',
      borderRadius: 99,
      background: 'rgba(16,185,129,0.12)',
      border: `1px solid rgba(16,185,129,0.3)`,
      fontSize: 10,
      fontFamily: 'Space Mono, monospace',
      color: C.green,
      letterSpacing: 1,
    }}>
      <span style={{
        width: 6,
        height: 6,
        borderRadius: '50%',
        background: C.green,
        display: 'inline-block',
        animation: 'pulse 2s infinite',
      }} />
      LIVE
    </div>
  );
}

// ── ThreatDot ─────────────────────────────────────────────────────────────────
/**
 * Small colored severity dot.
 * @param {string} color — dot fill color
 * @param {number} size  — diameter in px (default 8)
 */
export function ThreatDot({ color = C.red, size = 8 }) {
  return (
    <span style={{
      display: 'inline-block',
      width: size,
      height: size,
      borderRadius: '50%',
      background: color,
      flexShrink: 0,
      boxShadow: `0 0 ${size}px ${color}88`,
    }} />
  );
}

// ── Spinner ───────────────────────────────────────────────────────────────────
/**
 * Simple CSS spinner.
 * @param {number} size  — diameter in px (default 20)
 * @param {string} color — border color (default accent)
 */
export function Spinner({ size = 20, color = C.accent }) {
  return (
    <div style={{
      width: size,
      height: size,
      borderRadius: '50%',
      border: `2px solid ${C.border}`,
      borderTopColor: color,
      animation: 'spin 0.7s linear infinite',
    }} />
  );
}

// ── Divider ───────────────────────────────────────────────────────────────────
export function Divider({ style = {} }) {
  return (
    <hr style={{
      border: 'none',
      borderTop: `1px solid ${C.border}`,
      margin: '12px 0',
      ...style,
    }} />
  );
}
