/**
 * frontend/src/App.jsx
 * ─────────────────────
 * Phase 2 changes (minimal):
 *   1. Uses useAuth() hook to restore sessions from stored token on load
 *   2. Shows a loading screen while validating the stored token
 *   3. Passes real logout (clearAuth) to Dashboard
 *
 * Everything else (Landing, Dashboard, StyleInject) is UNCHANGED.
 */

import { useEffect, useState } from 'react';
import { StyleInject }  from './theme/StyleInject.jsx';
import { Landing }      from './pages/Landing.jsx';
import { Login }        from './pages/Login.jsx';
import { Dashboard }    from './layout/Dashboard.jsx';
import { useAuth }      from './auth/useAuth.js';
import { C }            from './theme/colors.js';

export default function App() {
  const { user, loading, logout } = useAuth();
  const [page, setPage] = useState('landing');  // 'landing' | 'login' | 'dashboard'

  // If a valid stored session is restored, skip straight to dashboard
  useEffect(() => {
    if (!loading && user) {
      setPage('dashboard');
    }
  }, [loading, user]);

  // Brief loading screen while validating stored token
  if (loading) {
    return (
      <>
        <StyleInject />
        <div style={{
          minHeight: '100vh', display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center', background: C.bg,
        }}>
          <div style={{
            width: 48, height: 48,
            background: `linear-gradient(135deg,${C.accent},${C.purple})`,
            borderRadius: 12, display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: 24,
            boxShadow: `0 0 24px ${C.accent}55`,
            animation: 'pulse 2s infinite', marginBottom: 16,
          }}>🛡</div>
          <div className="orb" style={{ color: C.accent, fontSize: 11, letterSpacing: 2 }}>
            INITIALIZING...
          </div>
        </div>
      </>
    );
  }

  function handleLogin(u) {
    setPage('dashboard');
    // user state is already set by useAuth hook's login/register functions
    // but we accept `u` here for the demo-access path (no hook)
    void u;
  }

  function handleLogout() {
    logout();          // clears token from storage
    setPage('landing');
  }

  return (
    <>
      <StyleInject />
      {page === 'landing'   && <Landing   onLogin={() => setPage('login')} />}
      {page === 'login'     && <Login     onLogin={handleLogin} onBack={() => setPage('landing')} />}
      {page === 'dashboard' && <Dashboard user={user} onLogout={handleLogout} />}
    </>
  );
}
