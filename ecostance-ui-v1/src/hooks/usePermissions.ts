import { useState, useEffect } from 'react';
import { rbacAPI } from '../services/api';

interface UserPermissions {
  permissions: string[];
  roles: Array<{
    id: string;
    name: string;
    permissions: string[];
  }>;
  system_role?: string;
}

export function usePermissions() {
  const [permissions, setPermissions] = useState<UserPermissions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPermissions();
  }, []);

  const loadPermissions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await rbacAPI.permissions.getMyPermissions() as UserPermissions;
      setPermissions(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load permissions');
      console.error('Failed to load user permissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const hasPermission = (permission: string): boolean => {
    if (!permissions) return false;
    return permissions.permissions.includes(permission);
  };

  const hasAnyPermission = (permissionList: string[]): boolean => {
    if (!permissions) return false;
    return permissionList.some(permission => permissions.permissions.includes(permission));
  };

  const hasAllPermissions = (permissionList: string[]): boolean => {
    if (!permissions) return false;
    return permissionList.every(permission => permissions.permissions.includes(permission));
  };

  const hasRole = (roleName: string): boolean => {
    if (!permissions) return false;
    return permissions.roles.some(role => role.name === roleName);
  };

  const isSystemAdmin = (): boolean => {
    if (!permissions) return false;
    return permissions.system_role === 'super_admin' || permissions.system_role === 'tenant_admin';
  };

  const isSuperAdmin = (): boolean => {
    if (!permissions) return false;
    return permissions.system_role === 'super_admin';
  };

  const canManageRoles = (): boolean => {
    return hasPermission('TENANT_MANAGE_USERS') || isSystemAdmin();
  };

  const canViewTenantSettings = (): boolean => {
    return hasPermission('TENANT_VIEW') || isSystemAdmin();
  };

  const canManageTenantSettings = (): boolean => {
    return hasPermission('TENANT_MANAGE') || isSystemAdmin();
  };

  return {
    permissions,
    loading,
    error,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    isSystemAdmin,
    isSuperAdmin,
    canManageRoles,
    canViewTenantSettings,
    canManageTenantSettings,
    refresh: loadPermissions,
  };
}