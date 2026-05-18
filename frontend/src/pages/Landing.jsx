/**
 * src/pages/Landing.jsx
 * ──────────────────────
 * FraudShield AI — Hero landing page.
 *
 * Shown to unauthenticated users before they log in.
 * Communicates the product value proposition with a cybersecurity/SOC aesthetic.
 *
 * Props:
 *   onLogin — callback to navigate to the login page
 */

import { C } from '../theme/colors.js';

export function Landing({ onLogin }) {
  return (
    <div style={{
      minHeight: '100vh',
      background: C.bg,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 24px',
      position: 'relative',
      overflow: 'hidden',
    }}>

      {/* ── Background grid decoration ──────────────────────────────────── */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        backgroundImage: `
          linear-gradient(${C.border}22 1px, transparent 1px),
          linear-gradient(90deg, ${C.border}22 1px, transparent 1px)
        `,
        backgroundSize: '48px 48px',
        opacity: 0.4,
      }} />

      {/* ── Glow orb ────────────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute',
        top: '20%', left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 400, height: 400,
        borderRadius: '50%',
        background: `radial-gradient(circle, ${C.accentGlow} 0%, transparent 70%)`,
        pointerEvents: 'none',
      }} />

      {/* ── Content ─────────────────────────────────────────────────────── */}
      <div style={{ position: 'relative', textAlign: 'center', maxWidth: 640 }}>

        {/* Logo */}
        <div style={{
          width: 72, height: 72,
          background: `linear-gradient(135deg, ${C.accent}, ${C.purple})`,
          borderRadius: 18,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 36,
          margin: '0 auto 24px',
          boxShadow: `0 0 40px ${C.accent}44`,
          animation: 'pulse 3s infinite',
        }}>
          🛡
        </div>

        {/* Brand */}
        <div className="orb" style={{
          fontSize: 13, letterSpacing: 4, color: C.accent, marginBottom: 16,
        }}>
          FRAUDSHIELD AI
        </div>

        {/* Headline */}
        <h1 style={{
          fontSize: 'clamp(28px, 5vw, 48px)',
          fontWeight: 700,
          color: C.text,
          lineHeight: 1.2,
          marginBottom: 20,
        }}>
          AI-Powered Financial<br />
          <span style={{ color: C.accent }}>Fraud Detection</span>
        </h1>

        {/* Subtitle */}
        <p style={{
          fontSize: 16,
          color: C.muted,
          lineHeight: 1.7,
          marginBottom: 40,
          maxWidth: 480,
          margin: '0 auto 40px',
        }}>
          Real-time fraud detection, SIEM analytics, and ML-powered risk scoring
          for financial security operations teams.
        </p>

        {/* CTA */}
        <button
          onClick={onLogin}
          style={{
            padding: '14px 40px',
            background: `linear-gradient(135deg, ${C.accent}, ${C.purple})`,
            border: 'none',
            borderRadius: 8,
            color: '#0f1117',
            fontSize: 14,
            fontWeight: 700,
            fontFamily: 'Space Mono, monospace',
            letterSpacing: 1,
            cursor: 'pointer',
            boxShadow: `0 0 24px ${C.accent}44`,
            transition: 'transform 0.15s, box-shadow 0.15s',
          }}
          onMouseEnter={e => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = `0 4px 32px ${C.accent}66`;
          }}
          onMouseLeave={e => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = `0 0 24px ${C.accent}44`;
          }}
        >
          ACCESS DASHBOARD →
        </button>

        {/* Feature pills */}
        <div style={{
          display: 'flex', flexWrap: 'wrap', gap: 10,
          justifyContent: 'center', marginTop: 48,
        }}>
          {[
            '🤖 ML Fraud Detection',
            '📊 Live Analytics',
            '🚨 Alert Management',
            '🔐 JWT Auth',
            '⚡ FastAPI Backend',
          ].map((f) => (
            <span key={f} style={{
              padding: '6px 14px',
              borderRadius: 99,
              border: `1px solid ${C.border}`,
              fontSize: 12,
              color: C.muted,
              background: C.surface,
            }}>
              {f}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
