/**
 * src/services/apiClient.js
 * ──────────────────────────
 * Single axios instance shared by all services.
 *
 * - local dev uses /api → Vite proxy → FastAPI :8000
 * - production uses VITE_API_BASE_URL or VITE_API_URL
 * - Automatically attaches JWT token from storage on every request
 * - On 401 → clears stale token and reloads to login screen
 */

import axios from 'axios';

const TOKEN_KEYS = ['fs_token'];  // matches authApi.js storage keys

function getToken() {
  for (const k of TOKEN_KEYS) {
    const t = localStorage.getItem(k) || sessionStorage.getItem(k);
    if (t) return t;
  }
  return null;
}

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '/api';
const BASE_URL = rawBaseUrl.replace(/\/+$/, '');

if (import.meta.env.PROD && /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/.test(BASE_URL)) {
  // Keep the app running, but make a bad production env obvious in browser logs.
  console.error(
    `Invalid production API base URL: ${BASE_URL}. ` +
      'Set VITE_API_BASE_URL to your deployed backend URL, for example https://fraudshield-ai-backend.onrender.com/api.',
  );
}

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token before every request
apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401 clear storage and reload (forces login screen)
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const method = err.config?.method?.toUpperCase() || 'REQUEST';
    const url = `${err.config?.baseURL || ''}${err.config?.url || ''}`;
    const status = err.response?.status || 'NETWORK';
    console.error(`[API ${status}] ${method} ${url}`, err.response?.data || err.message);

    if (err.response?.status === 401) {
      ['fs_token', 'fs_user'].forEach((k) => {
        localStorage.removeItem(k);
        sessionStorage.removeItem(k);
      });
      window.location.reload();
    }
    return Promise.reject(err);
  },
);
