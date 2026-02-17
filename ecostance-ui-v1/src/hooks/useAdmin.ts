import { useState, useCallback } from 'react';
import { adminAPI, tenantsAPI } from '../services/api';
import type {
  SystemHealth,
  DashboardSummary,
  TenantSearchResult,
  TenantStorage,
  TenantActivity,
  Tenant
} from '../services/api.types';

export function useAdmin() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const getSystemHealth = useCallback(async (): Promise<SystemHealth | null> => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.getSystemHealth() as SystemHealth;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch system health');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getDashboardSummary = useCallback(async (): Promise<DashboardSummary | null> => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.getDashboardSummary() as DashboardSummary;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch dashboard summary');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const searchTenants = useCallback(async (
    query: string,
    limit = 20
  ): Promise<TenantSearchResult | null> => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.searchTenants(query, limit) as TenantSearchResult;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to search tenants');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const listAllTenants = useCallback(async (
    skip = 0,
    limit = 100
  ): Promise<Tenant[] | null> => {
    try {
      setLoading(true);
      setError(null);
      return await tenantsAPI.listTenants(skip, limit) as Tenant[];
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to list tenants');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getTenantStorage = useCallback(async (tenantId: string): Promise<TenantStorage | null> => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.getTenantStorage(tenantId) as TenantStorage;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch tenant storage');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getTenantActivity = useCallback(async (
    tenantId: string,
    days = 7
  ): Promise<TenantActivity | null> => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.getTenantActivity(tenantId, days) as TenantActivity;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch tenant activity');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTenantTier = useCallback(async (tenantId: string, tier: string) => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.updateTenantTier(tenantId, tier);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update tenant tier');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const suspendTenant = useCallback(async (tenantId: string) => {
    try {
      setLoading(true);
      setError(null);
      return await tenantsAPI.deactivateTenant(tenantId);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to suspend tenant');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const reactivateTenant = useCallback(async (tenantId: string) => {
    try {
      setLoading(true);
      setError(null);
      return await tenantsAPI.activateTenant(tenantId);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to reactivate tenant');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTenant = useCallback(async (
    tenantId: string,
    softDelete = true
  ) => {
    try {
      setLoading(true);
      setError(null);
      // Map softDelete toggle to hardDelete param in tenantsAPI
      const hardDelete = !softDelete;
      return await tenantsAPI.deleteTenant(tenantId, hardDelete);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete tenant');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const exportTenantData = useCallback(async (tenantId: string, exportPath?: string) => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.exportTenantData(tenantId, exportPath);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to export tenant data');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const cleanupSessions = useCallback(async (maxAgeHours = 24) => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.cleanupSessions(maxAgeHours);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to cleanup sessions');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const cleanupTempFiles = useCallback(async (maxAgeDays = 7) => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.cleanupTempFiles(maxAgeDays);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to cleanup temp files');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const runDailyCleanup = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      return await adminAPI.runDailyCleanup();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to run daily cleanup');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getSystemHealth,
    getDashboardSummary,
    searchTenants,
    listAllTenants,
    getTenantStorage,
    getTenantActivity,
    updateTenantTier,
    suspendTenant,
    reactivateTenant,
    deleteTenant,
    exportTenantData,
    cleanupSessions,
    cleanupTempFiles,
    runDailyCleanup,
  };
}
