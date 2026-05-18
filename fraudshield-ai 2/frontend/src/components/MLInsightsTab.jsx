/**
 * src/components/MLInsightsTab.jsx
 * ─────────────────────────────────
 * Phase 5: ML-powered analytics panel.
 *
 * Shows:
 * - Fraud Trends chart (over time)
 * - Risk Score Distribution histogram
 * - Per-Type Risk Breakdown table
 * - Model Info card (training metrics)
 *
 * All data from new ML analytics endpoints.
 * Preserves existing app structure — add this tab alongside AnalyticsTab.
 */

import { useEffect, useState } from 'react';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';
import { getFraudTrends, getRiskDistribution, getTypeRisk, getModelInfo } from '../services/mlService.js';

// ── Simple palette (no theme dependency) ──────────────────────────────────
const C = {
  bg:      '#0f1117',
  card:    '#1a1d27',
  border:  '#2a2d3e',
  text:    '#e2e8f0',
  muted:   '#64748b',
  accent:  '#6366f1',
  green:   '#10b981',
  red:     '#ef4444',
  yellow:  '#f59e0b',
  orange:  '#f97316',
};

// ── Sub-components ────────────────────────────────────────────────────────

function Card({ title, children, badge }) {
  return (
    <div style={{
      background: C.card, border: `1px solid ${C.border}`,
      borderRadius: 12, padding: '20px 24px', marginBottom: 24,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
        <h3 style={{ color: C.text, fontSize: 15, fontWeight: 600, margin: 0 }}>{title}</h3>
        {badge && (
          <span style={{
            background: C.accent + '22', color: C.accent,
            padding: '2px 8px', borderRadius: 20, fontSize: 11, fontWeight: 600,
          }}>{badge}</span>
        )}
      </div>
      {children}
    </div>
  );
}

function MetricPill({ label, value, color }) {
  return (
    <div style={{
      background: C.bg, border: `1px solid ${C.border}`,
      borderRadius: 8, padding: '10px 16px', textAlign: 'center',
    }}>
      <div style={{ color: color || C.accent, fontSize: 22, fontWeight: 700 }}>{value}</div>
      <div style={{ color: C.muted, fontSize: 11, marginTop: 2 }}>{label}</div>
    </div>
  );
}

function ModelInfoCard({ info }) {
  if (!info) return null;

  if (info.status === 'not_trained') {
    return (
      <Card title="ML Model Status" badge="Not Trained">
        <div style={{ color: C.yellow, fontSize: 13 }}>
          ⚠️ Model not trained yet. Run: <code style={{ color: C.accent }}>python -m backend.ml_models.trainer</code>
        </div>
        <div style={{ color: C.muted, fontSize: 12, marginTop: 8 }}>
          The system is using rule-based scoring as a fallback. Training takes ~60s on 200k rows.
        </div>
      </Card>
    );
  }

  const m = info.metrics || {};
  const top5 = Object.entries(info.feature_importances || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <Card title="ML Model — Random Forest" badge="Trained ✓">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        <MetricPill label="AUC-ROC"   value={m.auc_roc}   color={C.green} />
        <MetricPill label="Precision" value={m.precision}  color={C.accent} />
        <MetricPill label="Recall"    value={m.recall}     color={C.yellow} />
        <MetricPill label="F1 Score"  value={m.f1}         color={C.orange} />
      </div>

      <div style={{ color: C.muted, fontSize: 12, marginBottom: 10 }}>
        Trained on {(info.trained_on_rows || 0).toLocaleString()} rows · {info.n_features} features
      </div>

      <div style={{ color: C.text, fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
        Top Feature Importances
      </div>
      {top5.map(([name, val]) => (
        <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <div style={{ color: C.muted, fontSize: 12, width: 180 }}>{name}</div>
          <div style={{ flex: 1, background: C.border, borderRadius: 4, height: 6 }}>
            <div style={{
              width: `${val * 100 * 5}%`, maxWidth: '100%',
              background: C.accent, borderRadius: 4, height: 6,
            }} />
          </div>
          <div style={{ color: C.text, fontSize: 12, width: 40 }}>{(val * 100).toFixed(1)}%</div>
        </div>
      ))}
    </Card>
  );
}

function TrendsChart({ data }) {
  if (!data?.trends?.length) return <div style={{ color: C.muted }}>No trend data</div>;

  const chartData = data.trends.map(t => ({
    period:     t.step_start,
    fraud_rate: t.fraud_rate,
    avg_risk:   t.avg_risk,
    total:      t.total,
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={chartData} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
        <XAxis dataKey="period" tick={{ fill: C.muted, fontSize: 11 }} />
        <YAxis yAxisId="left"  tick={{ fill: C.muted, fontSize: 11 }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fill: C.muted, fontSize: 11 }} />
        <Tooltip
          contentStyle={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8 }}
          labelStyle={{ color: C.text }}
        />
        <Legend wrapperStyle={{ color: C.muted, fontSize: 12 }} />
        <Line yAxisId="left"  type="monotone" dataKey="fraud_rate" stroke={C.red}    strokeWidth={2} dot={false} name="Fraud Rate %" />
        <Line yAxisId="right" type="monotone" dataKey="avg_risk"   stroke={C.yellow} strokeWidth={2} dot={false} name="Avg Risk Score" />
      </LineChart>
    </ResponsiveContainer>
  );
}

function RiskDistChart({ data }) {
  if (!data?.distribution?.length) return <div style={{ color: C.muted }}>No data</div>;

  const chartData = data.distribution.map(d => ({
    band:       d.band,
    legitimate: d.legitimate,
    fraud:      d.fraud_count,
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={chartData} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
        <XAxis dataKey="band" tick={{ fill: C.muted, fontSize: 10 }} />
        <YAxis tick={{ fill: C.muted, fontSize: 11 }} />
        <Tooltip
          contentStyle={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8 }}
          labelStyle={{ color: C.text }}
        />
        <Legend wrapperStyle={{ color: C.muted, fontSize: 12 }} />
        <Bar dataKey="legitimate" stackId="a" fill={C.green}  name="Legitimate" />
        <Bar dataKey="fraud"      stackId="a" fill={C.red}    name="Fraud" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function TypeRiskTable({ data }) {
  if (!data?.length) return <div style={{ color: C.muted }}>No data</div>;

  const sevColor = r => r >= 75 ? C.red : r >= 50 ? C.orange : r >= 25 ? C.yellow : C.green;

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
      <thead>
        <tr style={{ borderBottom: `1px solid ${C.border}` }}>
          {['Type','Total','Fraud','Fraud Rate','Avg Risk','Max Risk'].map(h => (
            <th key={h} style={{ padding: '8px 12px', color: C.muted, fontWeight: 500, textAlign: 'left' }}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map(row => (
          <tr key={row.type} style={{ borderBottom: `1px solid ${C.border}22` }}>
            <td style={{ padding: '10px 12px', color: C.accent, fontWeight: 600 }}>{row.type}</td>
            <td style={{ padding: '10px 12px', color: C.text }}>{row.total.toLocaleString()}</td>
            <td style={{ padding: '10px 12px', color: C.red }}>{row.fraud_count}</td>
            <td style={{ padding: '10px 12px', color: C.yellow }}>{row.fraud_rate}%</td>
            <td style={{ padding: '10px 12px', color: sevColor(row.avg_risk) }}>{row.avg_risk}</td>
            <td style={{ padding: '10px 12px', color: sevColor(row.max_risk) }}>{row.max_risk}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ── Main Component ────────────────────────────────────────────────────────

export function MLInsightsTab() {
  const [trends,   setTrends]   = useState(null);
  const [riskDist, setRiskDist] = useState(null);
  const [typeRisk, setTypeRisk] = useState(null);
  const [modelInfo,setModelInfo]= useState(null);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [t, r, tr, m] = await Promise.allSettled([
          getFraudTrends(20),
          getRiskDistribution(),
          getTypeRisk(),
          getModelInfo(),
        ]);
        if (t.status  === 'fulfilled') setTrends(t.value);
        if (r.status  === 'fulfilled') setRiskDist(r.value);
        if (tr.status === 'fulfilled') setTypeRisk(tr.value);
        if (m.status  === 'fulfilled') setModelInfo(m.value);
      } catch (e) {
        setError('Failed to load ML analytics. Is the backend running?');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return (
    <div style={{ color: C.muted, padding: 40, textAlign: 'center' }}>
      Loading ML analytics…
    </div>
  );

  if (error) return (
    <div style={{ color: C.red, padding: 40, textAlign: 'center' }}>{error}</div>
  );

  return (
    <div style={{ padding: '0 4px' }}>

      {/* Model Info */}
      <ModelInfoCard info={modelInfo} />

      {/* Fraud Trends */}
      <Card title="Fraud Trends Over Time" badge={`${trends?.buckets || 0} periods`}>
        <TrendsChart data={trends} />
      </Card>

      {/* Risk Distribution */}
      <Card title="Risk Score Distribution" badge="10-point bands">
        {riskDist?.summary && (
          <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
            <MetricPill label="Mean Risk"  value={riskDist.summary.mean_risk_score} color={C.accent} />
            <MetricPill label="Max Risk"   value={riskDist.summary.max_risk_score}  color={C.red} />
            <MetricPill label="Min Risk"   value={riskDist.summary.min_risk_score}  color={C.green} />
          </div>
        )}
        <RiskDistChart data={riskDist} />
      </Card>

      {/* Per-Type Risk */}
      <Card title="Risk Breakdown by Transaction Type">
        <TypeRiskTable data={typeRisk} />
      </Card>

    </div>
  );
}
