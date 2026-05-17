/**
 * frontend/src/services/authApi.js
 * ──────────────────────────────────
 * All auth-related API calls: login, register, logout, session restore.
 *
 * Token storage:
 *   - "remember me" ON  → localStorage  (persists across browser restarts)
 *   - "remember me" OFF → sessionStorage (cleared when tab closes)
 *
 * The stored token is sent automatically via the Authorization header
 * by the axios interceptor below.
 */

import axios from 'axios';

// ── Axios instance ─────────────────────────────────────────────────────────

export const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// Attach the JWT token to every request automatically
api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If backend returns 401, clear stale token and reload to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      clearAuth();
      window.location.reload(); // snap back to login
    }
    return Promise.reject(err);
  }
);

// ── Token helpers ──────────────────────────────────────────────────────────

const TOKEN_KEY = 'fs_token';
const USER_KEY  = 'fs_user';

/**
 * Save token + user object after login/register.
 * @param {string}  token      JWT string
 * @param {object}  user       {email, name, role}
 * @param {boolean} remember   true → localStorage, false → sessionStorage
 */
export function saveAuth(token, user, remember = false) {
  const store = remember ? localStorage : sessionStorage;
  store.setItem(TOKEN_KEY, token);
  store.setItem(USER_KEY, JSON.stringify(user));
}

/** Read token from whichever storage has it. */
export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY) || null;
}

/** Read the cached user object (avoids an extra /me call on reload). */
export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY) || sessionStorage.getItem(USER_KEY);
  try { return raw ? JSON.parse(raw) : null; } catch { return null; }
}

/** Remove all auth data (logout). */
export function clearAuth() {
  [localStorage, sessionStorage].forEach((s) => {
    s.removeItem(TOKEN_KEY);
    s.removeItem(USER_KEY);
  });
}

/** True if a token exists in storage (user was previously logged in). */
export function isAuthenticated() {
  return Boolean(getStoredToken());
}

// ── API calls ──────────────────────────────────────────────────────────────

/**
 * POST /api/auth/login
 * Returns { access_token, user: { email, name, role } }
 */
export async function loginApi({ email, password }) {
  const { data } = await api.post('/auth/login', { email, password });
  return data; // caller decides whether to save
}

/**
 * POST /api/auth/register
 * Returns { access_token, user: { email, name, role } }
 */
export async function registerApi({ email, name, password, role = 'analyst' }) {
  const { data } = await api.post('/auth/register', { email, name, password, role });
  return data;
}

/**
 * GET /api/auth/me
 * Re-validates the stored token and returns the current user.
 * Call on app load to verify the token is still valid.
 */
export async function meApi() {
  const { data } = await api.get('/auth/me');
  return data;
}
