/**
 * src/hooks/useAnalytics.js
 * ──────────────────────────
 * Fetches the analytics summary from GET /api/analytics/summary.
 * Falls back gracefully to null so the UI can show static PAYSIM data
 * if the backend endpoint isn't running yet.
 */

import { useEffect, useState } from 'react';
import { getAnalyticsSummary } from '../services/analyticsService.js';

export function useAnalytics() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    getAnalyticsSummary()
      .then((data) => {
        if (!cancelled) setSummary(data);
      })
      .catch((err) => {
        // Silently fall back — AnalyticsTab will use static PAYSIM data
        if (!cancelled) setError(err?.message || 'Analytics endpoint unavailable');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, []);

  return { summary, loading, error };
}
