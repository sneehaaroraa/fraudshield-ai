/**
 * src/theme/colors.js
 * ────────────────────
 * FraudShield AI — Central design token file.
 * All components import from here — change once, update everywhere.
 *
 * Cybersecurity / SOC terminal aesthetic:
 *   Dark navy background, neon cyan accent, muted grays.
 */

export const C = {
  // ── Backgrounds ──────────────────────────────────────────────────────────
  bg:      '#0f1117',          // page background — deep near-black navy
  surface: '#1a1d27',          // card / panel surface
  surfaceHover: '#1e2130',     // card hover state
  elevated: '#22263a',         // modals, dropdowns

  // ── Borders ───────────────────────────────────────────────────────────────
  border:  '#2a2d3e',          // standard border
  borderBright: '#3a3d52',     // highlighted border

  // ── Text ──────────────────────────────────────────────────────────────────
  text:    '#e2e8f0',          // primary text — light slate
  muted:   '#64748b',          // secondary / placeholder text
  dim:     '#475569',          // very muted labels

  // ── Brand Accent (cyan) ───────────────────────────────────────────────────
  accent:  '#00d4ff',          // neon cyan — primary interactive
  accentGlow: 'rgba(0,212,255,0.15)',   // glow background
  accentDim:  'rgba(0,212,255,0.08)',   // subtle tint

  // ── Purple ────────────────────────────────────────────────────────────────
  purple:  '#a855f7',          // ML / AI highlights
  purpleGlow: 'rgba(168,85,247,0.15)',

  // ── Status Colors ─────────────────────────────────────────────────────────
  green:   '#10b981',          // success / legitimate / resolved
  greenGlow: 'rgba(16,185,129,0.15)',

  yellow:  '#f59e0b',          // warning / medium severity
  yellowGlow: 'rgba(245,158,11,0.15)',

  red:     '#ef4444',          // danger / fraud / critical
  redGlow: 'rgba(239,68,68,0.15)',

  orange:  '#f97316',          // escalated / high severity
  orangeGlow: 'rgba(249,115,22,0.15)',
};

/**
 * Severity → color map.
 * Used by SeverityBadge, AlertsTab, and any component that needs
 * consistent severity coloring without duplicating logic.
 */
export const SEV_CLR = {
  CRITICAL: C.red,
  HIGH:     C.orange,
  MEDIUM:   C.yellow,
  LOW:      C.green,
};

/**
 * Alert status → color map.
 */
export const STATUS_CLR = {
  OPEN:          C.red,
  INVESTIGATING: C.yellow,
  ESCALATED:     C.orange,
  RESOLVED:      C.green,
};
