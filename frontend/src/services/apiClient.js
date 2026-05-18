/**
 * src/services/apiClient.js
 * ──────────────────────────
 * Single axios instance shared by all services.
 *
 * - baseURL points to /api → Vite proxies to FastAPI :8000
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

// In production (Vercel), VITE_API_BASE_URL points to the deployed backend.
// In local dev, Vite proxies /api → localhost:8000 (see vite.config.js).
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

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
