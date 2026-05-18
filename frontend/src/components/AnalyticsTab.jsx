/**
 * src/pages/AnalyticsTab.jsx
 * ───────────────────────────
 * Phase 4: top KPI cards now pull from GET /api/analytics/summary.
 * Charts still use PAYSIM static data (real chart data requires Phase 5 aggregation).
 *
 * Changes from original:
 *   - useAnalytics() hook fetches live DB summary (total, fraud, alerts, avg risk)
 *   - If backend is unavailable, static PAYSIM values are shown as fallback
 *   - By-type breakdown uses live data when available
 *   - Loading indicator on KPI cards only (charts load instantly)
 *
 * Preserved:
 *   - All chart components (SocBarChart, SocLineChart)
 *   - PAYSIM static chart data (amount stats, fraud over time)
 *   - All grid layouts and typography
 */

import { C } from '../theme/colors.js';
import { PAYSIM } from '../data/paysim-summary.js';
import { SocBarChart, SocLineChart } from '../components/charts/SocCharts.jsx';
import { SeverityBadge } from '../components/SeverityBadge.jsx';
import { LoadingState } from '../components/State.jsx';
import { useAnalytics } from '../hooks/useAnalytics.js';

// Severity color map for the by_severity breakdown
const SEV_COLOR = { CRITICAL: C.red, HIGH: C.yellow, MEDIUM: C.accent, LOW: C.green };

export function AnalyticsTab() {
  const { summary, loading } = useAnalytics();
  const ot = PAYSIM.fraud_over_time;

  // ── Live KPIs (fall back to PAYSIM statics when backend is down) ───────────

  const kpis = [
    {
      label: 'Total Transactions (DB)',
      val:   summary ? summary.total_transactions.toLocaleString() : '5,000',
      color: C.accent,
      sub:   summary ? 'from SQLite' : 'sample dataset',
    },
    {
      label: 'Fraud Detected (DB)',
      val:   summary ? summary.total_fraud.toLocaleString() : PAYSIM.overview.fraud_total.toLocaleString(),
      color: C.red,
      sub:   summary ? `${summary.fraud_rate_pct}% fraud rate` : `${PAYSIM.overview.fraud_rate}% fraud rate`,
    },
    {
      label: 'Avg Risk Score',
      val:   summary ? `${summary.avg_risk_score}/99` : '—',
      color: C.yellow,
      sub:   'across all scored transactions',
    },
    {
      label: 'Open Alerts',
      val:   summary ? summary.open_alerts.toLocaleString() : '—',
      color: C.red,
      sub:   summary ? `${summary.critical_alerts} critical` : 'connect backend',
    },
  ];

  // ── By-type data: prefer live, fall back to PAYSIM ──────────────────────────
  const byTypeData = summary?.by_type?.length
    ? summary.by_type.map((r) => ({
        type:        r.type,
        fraud_count: r.fraud_count,
        fraud_rate:  Number(r.fraud_rate.toFixed(2)),
      }))
    : PAYSIM.fraud_by_type;

  // ── By-severity from live data ───────────────────────────────────────────────
  const bySev = summary?.by_severity || [];

  return (
    <div className="fadein">
      <div style={{ marginBottom: 22 }}>
        <h2 className="orb" style={{ fontSize: 18, fontWeight: 700, letterSpacing: 1 }}>
          FRAUD <span style={{ color: C.accent }}>ANALYTICS</span>
        </h2>
        <div style={{ fontSize: 11, color: C.muted, marginTop: 3, fontFamily: 'Space Mono' }}>
          {summary
            ? `Live DB metrics · ${summary.total_transactions.toLocaleString()} transactions scored`
            : 'PaySim static + connecting to backend…'}
        </div>
      </div>

      {/* Live KPI cards */}
      {loading ? (
        <LoadingState label="Fetching analytics from backend..." />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14, marginBottom: 20 }}>
          {kpis.map((s) => (
            <div key={s.label} className="card" style={{ padding: 16 }}>
              <div style={{ fontSize: 10, color: C.muted, fontFamily: 'Space Mono', letterSpacing: 0.8, marginBottom: 8 }}>
                {s.label}
              </div>
              <div className="orb" style={{ fontSize: 22, fontWeight: 900, color: s.color }}>
                {s.val}
              </div>
              <div style={{ fontSize: 11, color: C.muted, marginTop: 4 }}>{s.sub}</div>
            </div>
          ))}
        </div>
      )}

      {/* Alert severity breakdown (live) */}
      {bySev.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginBottom: 20 }}>
          {bySev.map((s) => (
            <div
              key={s.severity}
              className="card"
              style={{ padding: 14, borderLeft: `3px solid ${SEV_COLOR[s.severity] || C.muted}` }}
            >
              <SeverityBadge level={s.severity} small />
              <div className="orb" style={{ fontSize: 20, fontWeight: 900, color: SEV_COLOR[s.severity], marginTop: 8 }}>
                {s.count}
              </div>
              <div style={{ fontSize: 10, color: C.muted }}>alerts</div>
            </div>
          ))}
        </div>
      )}

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>

        {/* Fraud over time */}
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: C.text, fontFamily: 'Space Mono', letterSpacing: 1, marginBottom: 16 }}>
            FRAUD CASES OVER TIME (STEP = HOUR)
          </div>
          <SocLineChart
            data={ot}
            xKey="step"
            lines={[
              { dataKey: 'fraud', name: 'Fraud',  color: C.red },
              { dataKey: 'total', name: 'Total',  color: C.accent },
            ]}
            height={220}
          />
        </div>

        {/* Fraud by type — live when available */}
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: C.text, fontFamily: 'Space Mono', letterSpacing: 1, marginBottom: 16 }}>
            FRAUD BY TRANSACTION TYPE {summary ? '· LIVE DB' : '· PAYSIM STATIC'}
          </div>
          <SocBarChart
            data={byTypeData}
            xKey="type"
            bars={[
              { dataKey: 'fraud_count', name: 'Fraud Cases', color: C.red    },
              { dataKey: 'fraud_rate',  name: 'Rate %',      color: C.yellow },
            ]}
            height={220}
          />
        </div>
      </div>

      {/* Amount stats — static (preserved from original) */}
      <div className="card" style={{ padding: 20 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: C.text, fontFamily: 'Space Mono', letterSpacing: 1, marginBottom: 16 }}>
          AMOUNT STATISTICS — FRAUD vs ALL TRANSACTIONS
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
          {[
            { label: 'Mean Amount',   fraud: `$${(PAYSIM.amount_stats.mean_fraud / 1000).toFixed(1)}K`,   all: `$${(PAYSIM.amount_stats.mean_all / 1000).toFixed(1)}K`,   ratio: '8.2x higher' },
            { label: 'Median Amount', fraud: `$${(PAYSIM.amount_stats.median_fraud / 1000).toFixed(1)}K`, all: `$${(PAYSIM.amount_stats.median_all / 1000).toFixed(1)}K`, ratio: '5.9x higher' },
            { label: 'Maximum',       fraud: '$10,000,000',                                                all: '$92,445,517',                                             ratio: 'Capped at $10M' },
          ].map((s) => (
            <div key={s.label} style={{ background: C.surface, borderRadius: 5, padding: 16 }}>
              <div style={{ fontSize: 11, color: C.muted, fontFamily: 'Space Mono', marginBottom: 12 }}>{s.label}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 12, color: C.muted }}>Fraud Txns</span>
                <span className="orb" style={{ fontSize: 14, fontWeight: 900, color: C.red }}>{s.fraud}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 12, color: C.muted }}>All Txns</span>
                <span className="orb" style={{ fontSize: 14, fontWeight: 900, color: C.green }}>{s.all}</span>
              </div>
              <div style={{ padding: '5px 8px', background: C.redGlow, border: `1px solid ${C.red}22`, borderRadius: 3, fontSize: 10, color: C.red, fontFamily: 'Space Mono' }}>
                {s.ratio}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
