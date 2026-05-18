/**
 * frontend/src/auth/useAuth.js
 * ─────────────────────────────
 * Central auth state hook. Use this anywhere you need user info or auth actions.
 *
 * Usage:
 *   const { user, login, logout, loading } = useAuth();
 *
 * On app boot:
 *   1. Checks localStorage/sessionStorage for a stored token
 *   2. If found, calls /api/auth/me to validate it
 *   3. Sets user state (or clears stale token if expired)
 */

import { useState, useEffect, useCallback } from 'react';
import {
  loginApi,
  registerApi,
  meApi,
  saveAuth,
  clearAuth,
  getStoredUser,
  getStoredToken,
} from '../services/authApi';

export function useAuth() {
  const [user,    setUser]    = useState(null);
  const [loading, setLoading] = useState(true);  // true on first load while we validate token
  const [error,   setError]   = useState(null);

  // ── Restore session on app load ──────────────────────────────────────────

  useEffect(() => {
    const restore = async () => {
      const token = getStoredToken();

      if (!token) {
        setLoading(false);
        return;
      }

      // Try cached user first (instant), then verify with backend
      const cached = getStoredUser();
      if (cached) setUser(cached);

      try {
        const fresh = await meApi(); // validates token server-side
        setUser(fresh);
      } catch {
        // Token is expired or invalid — clear it and force login
        clearAuth();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    restore();
  }, []);

  // ── Login ────────────────────────────────────────────────────────────────

  const login = useCallback(async ({ email, password, remember }) => {
    setError(null);
    const data = await loginApi({ email, password }); // throws on 401
    saveAuth(data.access_token, data.user, remember);
    setUser(data.user);
    return data.user;
  }, []);

  // ── Register ─────────────────────────────────────────────────────────────

  const register = useCallback(async ({ email, name, password, remember }) => {
    setError(null);
    const data = await registerApi({ email, name, password });
    saveAuth(data.access_token, data.user, remember);
    setUser(data.user);
    return data.user;
  }, []);

  // ── Logout ───────────────────────────────────────────────────────────────

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
  }, []);

  return { user, loading, error, setError, login, register, logout };
}
