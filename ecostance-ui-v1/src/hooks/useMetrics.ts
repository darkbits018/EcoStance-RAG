import { useState, useCallback } from 'react';
import { metricsAPI, extendedMetricsAPI } from '../services/api';
import type { 
  TenantMetrics, 
  QueryMetrics, 
  ErrorMetrics, 
  AlertsResponse,
  StorageMetricRecord 
} from '../services/api.types';

export function useMetrics() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const getTenantMetrics = useCallback(async (
    metricType = 'daily',
    days = 30
  ): Promise<TenantMetrics | null> => {
    try {
      setLoading(true);
      setError(null);
      return await metricsAPI.getTenantMetrics(metricType, days) as TenantMetrics;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch tenant metrics');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getStorageMetrics = useCallback(async (days = 30): Promise<StorageMetricRecord[] | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await extendedMetricsAPI.getStorageMetrics(days) as { data: StorageMetricRecord[] };
      return response.data;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch storage metrics');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getQueryMetrics = useCallback(async (days = 7): Promise<QueryMetrics | null> => {
    try {
      setLoading(true);
      setError(null);
      return await extendedMetricsAPI.getQueryMetrics(days) as QueryMetrics;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch query metrics');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getErrorMetrics = useCallback(async (days = 7): Promise<ErrorMetrics | null> => {
    try {
      setLoading(true);
      setError(null);
      return await extendedMetricsAPI.getErrorMetrics(days) as ErrorMetrics;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch error metrics');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getActiveAlerts = useCallback(async (): Promise<AlertsResponse | null> => {
    try {
      setLoading(true);
      setError(null);
      return await extendedMetricsAPI.getActiveAlerts() as AlertsResponse;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch active alerts');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getAlertHistory = useCallback(async (
    days = 7,
    severity?: string
  ): Promise<AlertsResponse | null> => {
    try {
      setLoading(true);
      setError(null);
      return await extendedMetricsAPI.getAlertHistory(days, severity) as AlertsResponse;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch alert history');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const exportMetrics = useCallback(async (format = 'csv', days = 30) => {
    try {
      setLoading(true);
      setError(null);
      
      if (format === 'csv') {
        const blob = await extendedMetricsAPI.exportMetrics(format, days) as Blob;
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `metrics-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        return true;
      } else {
        return await extendedMetricsAPI.exportMetrics(format, days);
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to export metrics');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getTenantMetrics,
    getStorageMetrics,
    getQueryMetrics,
    getErrorMetrics,
    getActiveAlerts,
    getAlertHistory,
    exportMetrics,
  };
}
