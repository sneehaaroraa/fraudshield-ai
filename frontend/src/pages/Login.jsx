/**
 * frontend/src/pages/Login.jsx
 * ──────────────────────────────
 * Upgraded from Phase 1 simulation to REAL auth:
 *   - Calls POST /api/auth/login or /api/auth/register
 *   - Validates fields before submitting
 *   - Shows backend error messages
 *   - Password visibility toggle
 *   - Remember me checkbox
 *   - Forgot password link (UI only — Phase 4 feature)
 *   - Animated terminal log during auth
 *   - Preserves original SOC/cybersecurity aesthetic exactly
 */

import { useState, useRef } from 'react';
import { C } from '../theme/colors.js';
import { useAuth } from '../auth/useAuth.js';

// ── Tiny sub-components (keep file readable) ──────────────────────────────────

function Label({ children }) {
  return (
    <label style={{
      fontSize: 10, color: C.muted, fontFamily: 'Space Mono',
      letterSpacing: 1, display: 'block', marginBottom: 6,
    }}>
      {children}
    </label>
  );
}

function FieldError({ msg }) {
  if (!msg) return null;
  return (
    <div style={{ color: C.red, fontSize: 11, fontFamily: 'Space Mono', marginTop: 4 }}>
      ⚠ {msg}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function Login({ onLogin, onBack }) {
  const { login, register } = useAuth();

  const [mode,     setMode]     = useState('login');   // 'login' | 'register'
  const [form,     setForm]     = useState({ email: '', password: '', name: '' });
  const [showPwd,  setShowPwd]  = useState(false);
  const [remember, setRemember] = useState(false);
  const [loading,  setLoading]  = useState(false);
  const [logs,     setLogs]     = useState([]);
  const [errors,   setErrors]   = useState({});        // field-level validation
  const [apiError, setApiError] = useState('');        // backend error message

  const logRef = useRef(null);

  // ── Helpers ─────────────────────────────────────────────────────────────────

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const addLog = (msg, color = C.green) => {
    setLogs((l) => [...l.slice(-6), { msg, color, id: Date.now() + Math.random() }]);
    setTimeout(() => logRef.current?.scrollTo(0, 9999), 50);
  };

  // ── Validation ───────────────────────────────────────────────────────────────

  function validate() {
    const errs = {};
    if (!form.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      errs.email = 'Enter a valid email address';
    }
    if (form.password.length < 8) {
      errs.password = 'Password must be at least 8 characters';
    }
    if (mode === 'register' && !form.name.trim()) {
      errs.name = 'Full name is required';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  // ── Submit ───────────────────────────────────────────────────────────────────

  async function submit() {
    setApiError('');
    if (!validate()) return;

    setLoading(true);
    setLogs([]);

    // Terminal animation — matches original aesthetic
    addLog('[SYS] Initializing FraudShield Auth v3.2...');
    await delay(350);
    addLog('[NET] Connecting to secure auth endpoint...');
    await delay(350);

    try {
      let user;

      if (mode === 'login') {
        addLog('[AUTH] Verifying credentials with backend...');
        await delay(300);
        user = await login({ email: form.email, password: form.password, remember });
        addLog('[JWT] Token generated and stored securely ✓');
        await delay(200);
        addLog('[SYS] Access GRANTED — Welcome back, ' + (user.name || 'Analyst') + ' ✓', C.green);
      } else {
        addLog('[AUTH] Creating new analyst account...');
        await delay(300);
        user = await register({ email: form.email, name: form.name, password: form.password, remember });
        addLog('[DB]  User record created ✓');
        await delay(200);
        addLog('[SYS] Account ACTIVATED — Welcome to FraudShield AI ✓', C.green);
      }

      await delay(600);
      setLoading(false);
      onLogin(user);

    } catch (err) {
      // Show backend error message (e.g. "Invalid email or password")
      const msg = err.response?.data?.detail || 'Connection failed. Is the backend running?';
      addLog('[ERR] ' + msg, C.red);
      setApiError(msg);
      setLoading(false);
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !loading) submit();
  }

  // ── Demo access (no backend needed) ──────────────────────────────────────────

  async function demoAccess() {
    setLoading(true);
    setLogs([]);
    addLog('[DEMO] Loading demo analyst session...');
    await delay(800);
    addLog('[SYS] Demo access GRANTED ✓', C.green);
    await delay(500);
    setLoading(false);
    onLogin({ email: 'demo@fraudshield.ai', name: 'Demo Analyst', role: 'analyst' });
  }

  // ── Render ────────────────────────────────────────────────────────────────────

  return (
    <div
      className="grid-bg"
      style={{
        minHeight: '100vh', display: 'flex', alignItems: 'center',
        justifyContent: 'center', background: C.bg,
      }}
    >
      <div style={{ width: '100%', maxWidth: 440, padding: 20 }}>

        {/* Logo + title */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{
            width: 62, height: 62, margin: '0 auto 14px',
            background: `linear-gradient(135deg,${C.accent},${C.purple})`,
            borderRadius: 14, display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: 30,
            boxShadow: `0 0 28px ${C.accent}55`,
            animation: 'pulse 2.5s infinite',
          }}>🛡</div>
          <div className="orb" style={{ fontSize: 18, fontWeight: 900, color: C.accent, letterSpacing: 2 }}>
            FRAUDSHIELD AI
          </div>
          <div style={{ fontSize: 11, color: C.muted, marginTop: 4, fontFamily: 'Space Mono' }}>
            Cybersecurity Fraud Detection Platform
          </div>
        </div>

        {/* Card */}
        <div className="card" style={{ padding: 32 }}>

          {/* Login / Register tabs */}
          <div style={{ display: 'flex', borderBottom: `1px solid ${C.border}`, marginBottom: 26 }}>
            {['login', 'register'].map((m) => (
              <div
                key={m}
                onClick={() => { setMode(m); setErrors({}); setApiError(''); setLogs([]); }}
                style={{
                  flex: 1, textAlign: 'center', padding: '8px', cursor: 'pointer',
                  borderBottom: `2px solid ${mode === m ? C.accent : 'transparent'}`,
                  color: mode === m ? C.accent : C.muted,
                  fontSize: 12, fontFamily: 'Space Mono', letterSpacing: 1,
                  transition: 'all .2s',
                }}
              >
                {m === 'login' ? 'SIGN IN' : 'REGISTER'}
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

            {/* Name field (register only) */}
            {mode === 'register' && (
              <div>
                <Label>FULL NAME</Label>
                <input
                  className="input"
                  placeholder="Security Analyst"
                  value={form.name}
                  onChange={set('name')}
                  onKeyDown={handleKey}
                  style={errors.name ? { borderColor: C.red } : {}}
                />
                <FieldError msg={errors.name} />
              </div>
            )}

            {/* Email */}
            <div>
              <Label>EMAIL ADDRESS</Label>
              <input
                className="input"
                type="email"
                placeholder="analyst@fraudshield.ai"
                value={form.email}
                onChange={set('email')}
                onKeyDown={handleKey}
                style={errors.email ? { borderColor: C.red } : {}}
              />
              <FieldError msg={errors.email} />
            </div>

            {/* Password with visibility toggle */}
            <div>
              <Label>PASSWORD</Label>
              <div style={{ position: 'relative' }}>
                <input
                  className="input"
                  type={showPwd ? 'text' : 'password'}
                  placeholder="Min. 8 characters"
                  value={form.password}
                  onChange={set('password')}
                  onKeyDown={handleKey}
                  style={{
                    paddingRight: 42,
                    ...(errors.password ? { borderColor: C.red } : {}),
                  }}
                />
                {/* Eye toggle button */}
                <button
                  type="button"
                  onClick={() => setShowPwd((v) => !v)}
                  style={{
                    position: 'absolute', right: 11, top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer',
                    color: C.muted, fontSize: 15, padding: 2,
                  }}
                  title={showPwd ? 'Hide password' : 'Show password'}
                >
                  {showPwd ? '🙈' : '👁'}
                </button>
              </div>
              <FieldError msg={errors.password} />
            </div>

            {/* Remember me + Forgot password row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 7, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  style={{ accentColor: C.accent, width: 14, height: 14 }}
                />
                <span style={{ fontSize: 11, color: C.muted, fontFamily: 'Space Mono' }}>
                  Remember me
                </span>
              </label>

              {mode === 'login' && (
                <button
                  type="button"
                  onClick={() => setApiError('Password reset coming in Phase 4.')}
                  style={{
                    background: 'none', border: 'none', color: C.accent,
                    cursor: 'pointer', fontSize: 11, fontFamily: 'Space Mono',
                  }}
                >
                  Forgot password?
                </button>
              )}
            </div>

            {/* API-level error (e.g. wrong password) */}
            {apiError && (
              <div style={{
                background: C.redGlow, border: `1px solid ${C.red}44`,
                borderRadius: 4, padding: '9px 12px',
                color: C.red, fontSize: 11, fontFamily: 'Space Mono',
              }}>
                ⚠ {apiError}
              </div>
            )}

            {/* Terminal log */}
            {logs.length > 0 && (
              <div
                ref={logRef}
                style={{
                  background: '#020810', border: `1px solid ${C.border}`,
                  borderRadius: 4, padding: 12, maxHeight: 120, overflowY: 'auto',
                }}
              >
                {logs.map((l) => (
                  <div key={l.id} style={{
                    color: l.color, fontFamily: 'Space Mono',
                    fontSize: 10, lineHeight: 2,
                  }}>
                    {l.msg}
                  </div>
                ))}
              </div>
            )}

            {/* Submit button */}
            <button
              className="btn-p"
              onClick={submit}
              disabled={loading}
              style={{ marginTop: 4, padding: 13, opacity: loading ? 0.75 : 1 }}
            >
              {loading
                ? 'AUTHENTICATING...'
                : mode === 'login'
                  ? 'AUTHENTICATE →'
                  : 'CREATE ACCOUNT →'}
            </button>

            {/* Demo access */}
            <div style={{ textAlign: 'center' }}>
              <button
                type="button"
                onClick={demoAccess}
                disabled={loading}
                style={{
                  background: 'none', border: 'none',
                  color: C.muted, cursor: 'pointer',
                  fontSize: 11, fontFamily: 'Space Mono',
                  textDecoration: 'underline',
                }}
              >
                Quick Demo Access (no credentials needed)
              </button>
            </div>

          </div>
        </div>

        {/* Back link */}
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <button
            type="button"
            onClick={onBack}
            style={{
              background: 'none', border: 'none',
              color: C.muted, cursor: 'pointer',
              fontSize: 11, fontFamily: 'Space Mono',
            }}
          >
            ← Back
          </button>
        </div>

      </div>
    </div>
  );
}

// ── Utility ───────────────────────────────────────────────────────────────────

function delay(ms) {
  return new Promise((res) => setTimeout(res, ms));
}
