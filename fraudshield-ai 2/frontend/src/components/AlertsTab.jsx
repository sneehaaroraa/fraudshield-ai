/**
 * src/pages/AlertsTab.jsx
 * ─────────────────────────
 * Phase 4: switched from ALERTS_SEED hardcode → live useAlerts() hook.
 *
 * Changes from original:
 *   - useAlerts() replaces useState(ALERTS_SEED)
 *   - resolveAlert() calls PATCH /api/fraud/alerts/:id
 *   - severity filter chips now show real counts from backend
 *   - Loading + error states added
 *   - Analyst notes synced to backend via addNote()
 *   - Status badge → SeverityBadge component
 *
 * Preserved:
 *   - All layout, grid, card structure
 *   - INCIDENT_TIMELINE (still static — Phase 5 will make this dynamic)
 *   - Color scheme and typography exactly
 */

import { useState } from 'react';
import { C, SEV_CLR } from '../theme/colors.js';
import { INCIDENT_TIMELINE } from '../data/alerts.js';   // static timeline preserved
import { Badge, LivePill, ThreatDot } from '../components/atoms.jsx';
import { SeverityBadge } from '../components/SeverityBadge.jsx';
import { ErrorState, LoadingState } from '../components/State.jsx';
import { useAlerts } from '../hooks/useAlerts.js';

export function AlertsTab() {
  const { alerts, loading, error, filters, updateFilters, resolveAlert, addNote } = useAlerts();
  const [note, setNote] = useState('Initial triage: validate source account ownership and hold settlement for critical full-balance transfers.');
  const [selectedAlert, setSelectedAlert] = useState(null);

  // Count open alerts per severity for the KPI chips
  const counts = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].reduce((acc, sev) => {
    acc[sev] = alerts.filter((a) => a.sev === sev && a.status === 'OPEN').length;
    return acc;
  }, {});

  const openTotal = alerts.filter((a) => a.status === 'OPEN').length;

  // Save analyst note to backend when note changes and an alert is selected
  const saveNote = async () => {
    if (!selectedAlert) return;
    await addNote(selectedAlert, note);
  };

  return (
    <div className="fadein">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 22 }}>
        <div>
          <h2 className="orb" style={{ fontSize: 18, fontWeight: 700, letterSpacing: 1 }}>
            ALERT <span style={{ color: C.red }}>CENTER</span>
          </h2>
          <div style={{ fontSize: 11, color: C.muted, marginTop: 3, fontFamily: 'Space Mono' }}>
            {loading ? 'Loading alerts...' : `${openTotal} open · MITRE-mapped fraud detections · backend-live`}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <LivePill />
          {/* Status filter */}
          <div style={{ display: 'flex', gap: 6 }}>
            {['ALL', 'OPEN', 'INVESTIGATING', 'ESCALATED', 'RESOLVED'].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => updateFilters({ status: s })}
                style={{
                  padding: '5px 10px', borderRadius: 3, border: '1px solid',
                  fontFamily: 'Space Mono', fontSize: 9, cursor: 'pointer', letterSpacing: 0.5,
                  borderColor: filters.status === s ? C.accent : C.border,
                  background:  filters.status === s ? C.accentGlow : 'transparent',
                  color:       filters.status === s ? C.accent : C.muted,
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Severity KPI chips — clicking filters the list */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 18 }}>
        {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
          <button
            key={sev}
            type="button"
            className="card"
            style={{
              padding: 16, cursor: 'pointer', textAlign: 'left',
              borderColor: filters.severity === sev ? SEV_CLR[sev] : C.border,
            }}
            onClick={() => updateFilters({ severity: filters.severity === sev ? 'ALL' : sev })}
          >
            <div style={{ fontSize: 10, color: C.muted, fontFamily: 'Space Mono', letterSpacing: 0.8, marginBottom: 6 }}>
              {sev}
            </div>
            <div className="orb" style={{ fontSize: 26, fontWeight: 900, color: SEV_CLR[sev] }}>
              {loading ? '—' : counts[sev]}
            </div>
            <div style={{ fontSize: 11, color: C.muted }}>open alerts</div>
          </button>
        ))}
      </div>

      {/* Loading / Error states */}
      {loading && <LoadingState label="Loading alerts from  .." />}
      {error   && <ErrorState  message={`${error} — showing cached data if available`} />}

      {/* Main content */}
      {!loading && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.6fr .9fr', gap: 16 }}>

          {/* Alert feed table */}
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            {/* Table header */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '.7fr 1.5fr .8fr 1.2fr 1fr 1fr .8fr',
                padding: '10px 18px',
                borderBottom: `1px solid ${C.border}`,
                background: C.surface,
              }}
            >
              {['ID', 'ALERT TYPE', 'SEVERITY', 'MITRE', 'SOURCE', 'SCORE', 'ACTION'].map((h) => (
                <div key={h} style={{ fontSize: 9, color: C.muted, fontFamily: 'Space Mono', letterSpacing: 0.4 }}>
                  {h}
                </div>
              ))}
            </div>

            {/* Alert rows */}
            <div className="sb" style={{ maxHeight: 'calc(100vh - 390px)' }}>
              {alerts.length === 0 && !loading && (
                <div style={{ padding: 24, color: C.muted, fontFamily: 'Space Mono', fontSize: 11 }}>
                  No alerts match the current filters.
                </div>
              )}

              {alerts.map((a) => (
                <div
                  key={a.id}
                  className="trow"
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '.7fr 1.5fr .8fr 1.2fr 1fr 1fr .8fr',
                    padding: '12px 18px',
                    alignItems: 'center',
                    background: selectedAlert === a.id ? C.accentGlow : 'transparent',
                    cursor: 'pointer',
                  }}
                  onClick={() => setSelectedAlert(selectedAlert === a.id ? null : a.id)}
                >
                  {/* Alert ID */}
                  <div className="mono" style={{ fontSize: 10, color: C.muted }}>{a.id}</div>

                  {/* Type with pulse dot */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <ThreatDot color={SEV_CLR[a.sev]} size={7} />
                    <span style={{ fontSize: 12, fontWeight: 600, color: C.text }}>{a.type}</span>
                  </div>

                  {/* Severity badge */}
                  <div><SeverityBadge level={a.sev} /></div>

                  {/* MITRE technique */}
                  <div className="mono" style={{ fontSize: 10, color: C.yellow, lineHeight: 1.3 }}>
                    {a.mitre?.split(',')[0] || 'N/A'}
                  </div>

                  {/* Source TX ID */}
                  <div className="mono" style={{ fontSize: 10, color: C.muted }}>
                    {a.txId ? a.txId.slice(0, 12) : '—'}
                  </div>

                  {/* Risk score */}
                  <div className="mono" style={{ fontSize: 11, color: SEV_CLR[a.sev], fontWeight: 700 }}>
                    {Math.round(a.score)}/100
                  </div>

                  {/* Action button */}
                  <div onClick={(e) => e.stopPropagation()}>
                    {a.status === 'OPEN' ? (
                      <button
                        type="button"
                        className="btn-g"
                        style={{ padding: '4px 10px', fontSize: 9 }}
                        onClick={() => resolveAlert(a.id, 'INVESTIGATING')}
                      >
                        REVIEW
                      </button>
                    ) : a.status === 'INVESTIGATING' ? (
                      <button
                        type="button"
                        className="btn-r"
                        style={{ padding: '4px 10px', fontSize: 9 }}
                        onClick={() => resolveAlert(a.id, 'RESOLVED')}
                      >
                        RESOLVE
                      </button>
                    ) : (
                      <Badge color={C.green} bg={C.greenGlow}>✓ {a.status}</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
          </div>

          {/* Right panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

            {/* Analyst notes — saved to backend on blur */}
            <div className="card" style={{ padding: 18 }}>
              <div style={{ fontSize: 12, color: C.text, fontFamily: 'Space Mono', marginBottom: 8 }}>
                ANALYST NOTES
                {selectedAlert && (
                  <span style={{ fontSize: 9, color: C.muted, marginLeft: 8 }}>
                    · linked to {selectedAlert}
                  </span>
                )}
              </div>
              <textarea
                className="input"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                onBlur={saveNote}
                rows={8}
                aria-label="Analyst notes"
              />
              <button
                type="button"
                className="btn-g"
                style={{ width: '100%', marginTop: 8, padding: '7px', fontSize: 10 }}
                onClick={saveNote}
              >
                SAVE NOTE
              </button>
            </div>

            {/* Incident timeline — static, preserved from original */}
            <div className="card" style={{ padding: 18 }}>
              <div style={{ fontSize: 12, color: C.text, fontFamily: 'Space Mono', marginBottom: 12 }}>
                INCIDENT TIMELINE
              </div>
              {INCIDENT_TIMELINE.map((item) => (
                <div
                  key={item.time}
                  style={{ borderLeft: `2px solid ${C.accent}`, padding: '0 0 14px 12px' }}
                >
                  <div className="mono" style={{ fontSize: 10, color: C.accent }}>
                    {item.time} · {item.title}
                  </div>
                  <div style={{ fontSize: 12, color: C.muted, marginTop: 4 }}>{item.detail}</div>
                </div>
              ))}
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
