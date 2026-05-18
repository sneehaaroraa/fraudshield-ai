/**
 * src/hooks/useAlerts.js
 * ───────────────────────
 * Fetches live SIEM alerts from the FastAPI backend.
 * Replaces the hardcoded ALERTS_SEED array in AlertsTab.
 *
 * Features:
 *  - severity + status filtering (sent to backend as query params)
 *  - pagination
 *  - optimistic status update (UI updates instantly, then syncs)
 *  - auto-refresh every 30 seconds
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { getAlerts, updateAlert } from '../services/fraudService.js';

const REFRESH_MS = 30_000;  // poll every 30 seconds

export function useAlerts(initialFilters = {}) {
  const [filters, setFilters]       = useState({ severity: 'ALL', status: 'ALL', page: 1, pageSize: 20, ...initialFilters });
  const [alerts, setAlerts]         = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pageSize: 20, total: 0, totalPages: 1 });
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);

  const fetchAlerts = useCallback(async (f) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getAlerts(f);
      setAlerts(result.data || []);
      setPagination(result.pagination || { page: 1, pageSize: 20, total: 0, totalPages: 1 });
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Unable to load alerts');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on filter change
  useEffect(() => {
    fetchAlerts(filters);
  }, [filters.severity, filters.status, filters.page, filters.pageSize]);

  // Auto-refresh
  useEffect(() => {
    const id = setInterval(() => fetchAlerts(filters), REFRESH_MS);
    return () => clearInterval(id);
  }, [filters]);

  const updateFilters = (patch) =>
    setFilters((prev) => ({ ...prev, ...patch, page: patch.page ?? 1 }));

  /**
   * Optimistically update an alert's status in the UI, then persist to backend.
   * If the backend call fails, the UI state rolls back.
   */
  const resolveAlert = useCallback(async (alertId, newStatus = 'RESOLVED') => {
    const prev = [...alerts];
    // Optimistic update
    setAlerts((list) =>
      list.map((a) => (a.id === alertId ? { ...a, status: newStatus } : a)),
    );
    try {
      await updateAlert(alertId, { status: newStatus });
    } catch {
      // Rollback on failure
      setAlerts(prev);
    }
  }, [alerts]);

  const addNote = useCallback(async (alertId, notes) => {
    try {
      const updated = await updateAlert(alertId, { notes });
      setAlerts((list) => list.map((a) => (a.id === alertId ? { ...a, notes: updated.notes } : a)));
    } catch {
      // silent fail — notes are non-critical
    }
  }, []);

  return useMemo(() => ({
    alerts,
    pagination,
    filters,
    loading,
    error,
    updateFilters,
    resolveAlert,
    addNote,
    refresh: () => fetchAlerts(filters),
  }), [alerts, pagination, filters, loading, error]);
}
