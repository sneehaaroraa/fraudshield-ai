/**
 * src/components/charts/SocCharts.jsx
 * ─────────────────────────────────────
 * Reusable recharts wrappers with the FraudShield SOC color theme.
 * Used by AnalyticsTab and any future chart panels.
 *
 * Components:
 *   SocBarChart  — themed bar chart
 *   SocLineChart — themed line chart
 */

import {
  BarChart, Bar,
  LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer,
} from 'recharts';
import { C } from '../../theme/colors.js';

// ── Shared tooltip style ──────────────────────────────────────────────────────
const tooltipStyle = {
  contentStyle: {
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 6,
    fontFamily: 'Space Mono, monospace',
    fontSize: 11,
    color: C.text,
  },
  labelStyle: { color: C.muted, fontSize: 10 },
  cursor: { fill: C.accentDim },
};

// ── SocBarChart ───────────────────────────────────────────────────────────────
/**
 * SOC-themed bar chart wrapper.
 *
 * @param {Array}   data      — recharts-compatible data array
 * @param {string}  xKey      — key for X axis labels
 * @param {Array}   bars      — [{ key, color, label }]
 * @param {number}  height    — chart height in px (default 240)
 */
export function SocBarChart({
  data = [],
  xKey = 'name',
  bars = [{ key: 'value', color: C.accent, label: 'Value' }],
  height = 240,
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={{ fill: C.muted, fontSize: 10, fontFamily: 'Space Mono' }}
          axisLine={{ stroke: C.border }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: C.muted, fontSize: 10, fontFamily: 'Space Mono' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip {...tooltipStyle} />
        {bars.length > 1 && <Legend wrapperStyle={{ fontSize: 10, color: C.muted }} />}
        {bars.map((b) => (
          <Bar
            key={b.key}
            dataKey={b.key}
            name={b.label || b.key}
            fill={b.color || C.accent}
            radius={[3, 3, 0, 0]}
            maxBarSize={48}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── SocLineChart ──────────────────────────────────────────────────────────────
/**
 * SOC-themed line chart wrapper.
 *
 * @param {Array}   data    — recharts-compatible data array
 * @param {string}  xKey    — key for X axis labels
 * @param {Array}   lines   — [{ key, color, label }]
 * @param {number}  height  — chart height in px (default 240)
 */
export function SocLineChart({
  data = [],
  xKey = 'name',
  lines = [{ key: 'value', color: C.accent, label: 'Value' }],
  height = 240,
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={{ fill: C.muted, fontSize: 10, fontFamily: 'Space Mono' }}
          axisLine={{ stroke: C.border }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: C.muted, fontSize: 10, fontFamily: 'Space Mono' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip {...tooltipStyle} />
        {lines.length > 1 && <Legend wrapperStyle={{ fontSize: 10, color: C.muted }} />}
        {lines.map((l) => (
          <Line
            key={l.key}
            type="monotone"
            dataKey={l.key}
            name={l.label || l.key}
            stroke={l.color || C.accent}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: l.color || C.accent }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
