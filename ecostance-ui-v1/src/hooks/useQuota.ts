import { useState, useCallback, useEffect } from 'react';
import { quotaAPI } from '../services/api';
import type { QuotaStatus, QuotaLimits, QuotaUsage, QuotaHistoryRecord } from '../services/api.types';

export function useQuota() {
  const [status, setStatus] = useState<QuotaStatus | null>(null);
  const [limits, setLimits] = useState<QuotaLimits | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await quotaAPI.getStatus() as QuotaStatus;
      setStatus(data);
      return data;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch quota status');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchLimits = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await quotaAPI.getLimits() as QuotaLimits;
      setLimits(data);
      return data;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch quota limits');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getUsage = useCallback(async (period = 'daily'): Promise<QuotaUsage | null> => {
    try {
      setLoading(true);
      setError(null);
      return await quotaAPI.getUsage(period) as QuotaUsage;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch quota usage');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getHistory = useCallback(async (days = 30): Promise<QuotaHistoryRecord[] | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await quotaAPI.getHistory(days) as { data: QuotaHistoryRecord[] };
      return response.data;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch quota history');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-fetch status on mount
  useEffect(() => {
    fetchStatus();
    fetchLimits();
  }, [fetchStatus, fetchLimits]);

  // Helper functions to check quota warnings
  const isStorageWarning = useCallback(() => {
    return (status?.data?.storage?.usage_percent ?? 0) > 80;
  }, [status]);

  const isStorageCritical = useCallback(() => {
    return (status?.data?.storage?.usage_percent ?? 0) > 95;
  }, [status]);

  const isQueryWarning = useCallback(() => {
    return (status?.data?.queries?.daily_percent ?? 0) > 80;
  }, [status]);

  const isQueryCritical = useCallback(() => {
    return (status?.data?.queries?.daily_percent ?? 0) > 95;
  }, [status]);

  return {
    status,
    limits,
    loading,
    error,
    fetchStatus,
    fetchLimits,
    getUsage,
    getHistory,
    isStorageWarning,
    isStorageCritical,
    isQueryWarning,
    isQueryCritical,
  };
}
