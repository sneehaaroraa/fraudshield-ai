/**
 * src/layout/Dashboard.jsx
 * ─────────────────────────
 * FraudShield AI — Main application shell.
 *
 * Renders:
 *   - Top navigation bar with user info and logout
 *   - Tab switcher: Overview | Analytics | Alerts | ML Insights
 *   - Active tab content panel
 *
 * Props:
 *   user     — { email, name, role } from useAuth
 *   onLogout — callback to clear session and return to landing
 */

import { useState } from 'react';
import { C }              from '../theme/colors.js';
import { LivePill }       from '../components/atoms.jsx';
import { AnalyticsTab }   from '../components/AnalyticsTab.jsx';
import { AlertsTab }      from '../components/AlertsTab.jsx';
import { MLInsightsTab }  from '../components/MLInsightsTab.jsx';

// ── Tab config ────────────────────────────────────────────────────────────────
const TABS = [
  { id: 'analytics',   label: '📊 Analytics',    component: AnalyticsTab },
  { id: 'alerts',      label: '🚨 Alerts',        component: AlertsTab },
  { id: 'ml',          label: '🤖 ML Insights',   component: MLInsightsTab },
];

// ── NavTab button ─────────────────────────────────────────────────────────────
function NavTab({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: 'none',
        border: 'none',
        borderBottom: `2px solid ${active ? C.accent : 'transparent'}`,
        color: active ? C.accent : C.muted,
        fontFamily: 'Space Mono, monospace',
        fontSize: 11,
        letterSpacing: 1,
        padding: '12px 16px',
        cursor: 'pointer',
        transition: 'color 0.15s, border-color 0.15s',
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </button>
  );
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export function Dashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('analytics');

  const ActiveComponent = TABS.find(t => t.id === activeTab)?.component ?? AnalyticsTab;

  const roleBadgeColor = {
    admin:   C.red,
    analyst: C.accent,
    auditor: C.green,
  }[user?.role] ?? C.muted;

  return (
    <div style={{ minHeight: '100vh', background: C.bg, display: 'flex', flexDirection: 'column' }}>

      {/* ── Top Nav ───────────────────────────────────────────────────────── */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        height: 56,
        background: C.surface,
        borderBottom: `1px solid ${C.border}`,
        position: 'sticky', top: 0, zIndex: 100,
      }}>

        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 32, height: 32,
            background: `linear-gradient(135deg, ${C.accent}, ${C.purple})`,
            borderRadius: 8,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 16,
            boxShadow: `0 0 12px ${C.accent}44`,
          }}>🛡</div>

          <span className="orb" style={{
            fontSize: 11, letterSpacing: 3, color: C.accent,
          }}>
            FRAUDSHIELD AI
          </span>

          <LivePill />
        </div>

        {/* Tab nav — desktop */}
        <nav style={{ display: 'flex', gap: 0 }}>
          {TABS.map(t => (
            <NavTab
              key={t.id}
              label={t.label}
              active={activeTab === t.id}
              onClick={() => setActiveTab(t.id)}
            />
          ))}
        </nav>

        {/* User info + logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 12, color: C.text, fontWeight: 600 }}>
              {user?.name ?? 'Analyst'}
            </div>
            <div style={{
              fontSize: 10,
              fontFamily: 'Space Mono, monospace',
              color: roleBadgeColor,
              letterSpacing: 1,
            }}>
              {(user?.role ?? 'analyst').toUpperCase()}
            </div>
          </div>

          <button
            onClick={onLogout}
            style={{
              padding: '6px 14px',
              background: 'none',
              border: `1px solid ${C.border}`,
              borderRadius: 6,
              color: C.muted,
              fontSize: 11,
              fontFamily: 'Space Mono, monospace',
              cursor: 'pointer',
              transition: 'border-color 0.15s, color 0.15s',
              letterSpacing: 0.5,
            }}
            onMouseEnter={e => { e.target.style.borderColor = C.red; e.target.style.color = C.red; }}
            onMouseLeave={e => { e.target.style.borderColor = C.border; e.target.style.color = C.muted; }}
          >
            LOGOUT
          </button>
        </div>
      </header>

      {/* ── Main content ──────────────────────────────────────────────────── */}
      <main style={{ flex: 1, padding: '24px', maxWidth: 1400, margin: '0 auto', width: '100%' }}>
        <ActiveComponent />
      </main>

      {/* ── Footer ────────────────────────────────────────────────────────── */}
      <footer style={{
        padding: '12px 24px',
        borderTop: `1px solid ${C.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: 10,
        color: C.dim,
        fontFamily: 'Space Mono, monospace',
        letterSpacing: 0.5,
      }}>
        <span>FRAUDSHIELD AI v2.0.0 — SIEM PLATFORM</span>
        <span>{new Date().toUTCString().replace('GMT', 'UTC')} </span>
      </footer>
    </div>
  );
}
