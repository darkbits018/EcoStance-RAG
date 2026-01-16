import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { tenantsAPI, quotaAPI, rbacAPI } from '../services/api';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import RoleManagement from '../components/rbac/RoleManagement';
import UserManagement from '../components/rbac/UserManagement';
import { usePermissions } from '../hooks/usePermissions';
import { Settings, CreditCard, Bell, BarChart3, AlertCircle, Shield, Users, Plug } from 'lucide-react';
import GmailSettings from '../components/gmail/GmailSettings';
import DynamicsSettings from '../components/dynamics/DynamicsSettings';

interface Tenant {
  id: string;
  name: string;
  email: string;
  phone?: string;
  billing_tier: string;
  billing_status: string;
  created_at: string;
  gmail_config?: {
    is_connected: boolean;
    connected_email?: string;
  };
}

interface QuotaStatus {
  storage: { limit_bytes: number; used_bytes: number; usage_percent: number };
  queries: { daily_limit: number; daily_used: number; monthly_limit: number; monthly_used: number };
  documents: { limit: number; used: number; usage_percent: number };
}

export default function TenantSettingsPage() {
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState<'profile' | 'usage' | 'billing' | 'notifications' | 'rbac' | 'integrations'>((searchParams.get('tab') as any) || 'profile');
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [quotaStatus, setQuotaStatus] = useState<QuotaStatus | null>(null);
  const [error, setError] = useState('');

  const { canManageRoles, canViewTenantSettings, loading: permissionsLoading } = usePermissions();

  useEffect(() => {
    loadTenantData();
    loadQuotaStatus();
  }, []);

  const loadTenantData = async () => {
    try {
      const data = await tenantsAPI.getCurrentTenant() as Tenant;
      setTenant(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load tenant data');
    }
  };

  const loadQuotaStatus = async () => {
    try {
      const response = await quotaAPI.getStatus() as { data: QuotaStatus };
      setQuotaStatus(response.data);
    } catch (err: any) {
      console.error('Failed to load quota:', err);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-text flex items-center gap-2">
          <Settings className="w-6 h-6 text-primary" />
          Tenant Settings
        </h1>
        <p className="text-text-secondary mt-1">Manage your account settings and preferences</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-error/10 border border-error/20 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
          <p className="text-error">{error}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b border-border">
        <div className="flex gap-6">
          {[
            { id: 'profile', label: 'Profile', icon: Settings },
            { id: 'usage', label: 'Usage & Quotas', icon: BarChart3 },
            { id: 'rbac', label: 'Access Control', icon: Shield },
            { id: 'integrations', label: 'Integrations', icon: Plug },
            { id: 'billing', label: 'Billing', icon: CreditCard },
            { id: 'notifications', label: 'Notifications', icon: Bell },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`pb-3 px-1 border-b-2 transition-colors flex items-center gap-2 ${activeTab === tab.id
                ? 'border-primary text-primary'
                : 'border-transparent text-text-secondary hover:text-text'
                }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && tenant && (
        <Card className="p-6 bg-surface border-border">
          <h2 className="text-lg font-semibold mb-4 text-text">Profile Information</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Tenant ID</label>
              <input
                type="text"
                value={tenant.id}
                disabled
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-text"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Organization Name</label>
              <input
                type="text"
                value={tenant.name}
                disabled
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-text"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Email</label>
              <input
                type="email"
                value={tenant.email}
                disabled
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-text"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Phone</label>
              <input
                type="text"
                value={tenant.phone || 'Not provided'}
                disabled
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-text"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Member Since</label>
              <input
                type="text"
                value={formatDate(tenant.created_at)}
                disabled
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-text"
              />
            </div>
          </div>
        </Card>
      )}

      {/* Usage & Quotas Tab */}
      {activeTab === 'usage' && quotaStatus && (
        <div className="space-y-4">
          <Card className="p-6 bg-surface border-border">
            <h2 className="text-lg font-semibold mb-4 text-text">Storage Usage</h2>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Used</span>
                <span className="font-medium text-text">
                  {formatBytes(quotaStatus.storage.used_bytes)} / {formatBytes(quotaStatus.storage.limit_bytes)}
                </span>
              </div>
              <div className="w-full bg-background rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${Math.min(quotaStatus.storage.usage_percent, 100)}%` }}
                />
              </div>
              <p className="text-xs text-text-secondary">{quotaStatus.storage.usage_percent.toFixed(1)}% used</p>
            </div>
          </Card>

          <Card className="p-6 bg-surface border-border">
            <h2 className="text-lg font-semibold mb-4 text-text">Query Usage</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-2">Daily</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Used</span>
                    <span className="font-medium text-text">
                      {quotaStatus.queries.daily_used} / {quotaStatus.queries.daily_limit}
                    </span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <div
                      className="bg-success h-2 rounded-full"
                      style={{ width: `${Math.min((quotaStatus.queries.daily_used / quotaStatus.queries.daily_limit) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-2">Monthly</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Used</span>
                    <span className="font-medium text-text">
                      {quotaStatus.queries.monthly_used} / {quotaStatus.queries.monthly_limit}
                    </span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <div
                      className="bg-success h-2 rounded-full"
                      style={{ width: `${Math.min((quotaStatus.queries.monthly_used / quotaStatus.queries.monthly_limit) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6 bg-surface border-border">
            <h2 className="text-lg font-semibold mb-4 text-text">Document Usage</h2>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Documents</span>
                <span className="font-medium text-text">
                  {quotaStatus.documents.used} / {quotaStatus.documents.limit}
                </span>
              </div>
              <div className="w-full bg-background rounded-full h-2">
                <div
                  className="bg-accent h-2 rounded-full"
                  style={{ width: `${Math.min(quotaStatus.documents.usage_percent, 100)}%` }}
                />
              </div>
              <p className="text-xs text-text-secondary">{quotaStatus.documents.usage_percent.toFixed(1)}% used</p>
            </div>
          </Card>
        </div>
      )}

      {/* RBAC Tab */}
      {activeTab === 'rbac' && (
        <div className="space-y-6">
          {permissionsLoading && (
            <div className="p-4 bg-background border border-border rounded-lg">
              <p className="text-text-secondary">Loading permissions...</p>
            </div>
          )}

          {/* Debug Section */}
          <Card className="p-4 bg-warning/5 border-warning/20">
            <h3 className="text-sm font-medium text-warning mb-2">🔍 Debug Information</h3>
            <div className="text-xs space-y-1">
              <p>Permissions Loading: {permissionsLoading ? 'Yes' : 'No'}</p>
              <p>Can Manage Roles: {canManageRoles() ? 'Yes' : 'No'}</p>
              <p>Can View Tenant Settings: {canViewTenantSettings() ? 'Yes' : 'No'}</p>
              <Button
                size="sm"
                variant="outline"
                onClick={async () => {
                  try {
                    const debug = await rbacAPI.debug.getMyPermissions();
                    console.log('🔍 Current user permissions:', debug);
                    alert('Check console for permission details');
                  } catch (err) {
                    console.error('Debug failed:', err);
                    alert('Debug failed - check console');
                  }
                }}
                className="mt-2"
              >
                Check My Permissions
              </Button>
            </div>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-4 bg-surface border-border">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Shield className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-medium text-text">Role Management</h3>
                  <p className="text-sm text-text-secondary">Create and manage custom roles</p>
                </div>
              </div>
              <p className="text-xs text-text-secondary mb-2">
                {canManageRoles() ? 'You can manage roles' : 'View-only access'}
              </p>
            </Card>

            <Card className="p-4 bg-surface border-border">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-accent/10 rounded-lg">
                  <Users className="w-5 h-5 text-accent" />
                </div>
                <div>
                  <h3 className="font-medium text-text">User Management</h3>
                  <p className="text-sm text-text-secondary">Invite and manage team members</p>
                </div>
              </div>
              <p className="text-xs text-text-secondary mb-2">
                {canManageRoles() ? 'You can assign roles' : 'View-only access'}
              </p>
            </Card>
          </div>

          <RoleManagement />
          <UserManagement />
        </div>
      )}

      {/* Billing Tab */}
      {activeTab === 'billing' && tenant && (
        <Card className="p-6 bg-surface border-border">
          <h2 className="text-lg font-semibold mb-4 text-text">Billing Information</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Current Plan</label>
              <div className="px-3 py-2 border border-border rounded-lg bg-background capitalize text-text">
                {tenant.billing_tier}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Billing Status</label>
              <div className={`px-3 py-2 border rounded-lg capitalize ${tenant.billing_status === 'active' ? 'bg-success/10 text-success border-success/20' : 'bg-error/10 text-error border-error/20'
                }`}>
                {tenant.billing_status}
              </div>
            </div>
            <Button>Upgrade Plan</Button>
          </div>
        </Card>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <Card className="p-6 bg-surface border-border">
          <h2 className="text-lg font-semibold mb-4 text-text">Notification Preferences</h2>
          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 accent-primary" defaultChecked />
              <span className="text-sm text-text">Email notifications for quota warnings</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 accent-primary" defaultChecked />
              <span className="text-sm text-text">Email notifications for API errors</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 accent-primary" />
              <span className="text-sm text-text">Weekly usage reports</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 accent-primary" />
              <span className="text-sm text-text">Product updates and announcements</span>
            </label>
            <Button>Save Preferences</Button>
          </div>
        </Card>
      )}
      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <IntegrationsSection tenant={tenant} onRefresh={loadTenantData} />
      )}
    </div>
  );
}

function IntegrationsSection({ tenant, onRefresh }: { tenant: Tenant | null, onRefresh: () => Promise<void> }) {
  const { hasPermission, isSystemAdmin } = usePermissions();
  // Use lowercase permission strings to match backend response
  const canGmail = hasPermission('gmail:configure') || isSystemAdmin();
  const canDynamics = hasPermission('dynamics:configure') || isSystemAdmin();

  const [activeIntegration, setActiveIntegration] = useState<'gmail' | 'dynamics'>(canGmail ? 'gmail' : (canDynamics ? 'dynamics' : 'gmail'));

  if (!canGmail && !canDynamics) {
    return (
      <Card className="p-6 bg-surface border-border">
        <div className="flex items-center gap-3 text-warning">
          <AlertCircle className="w-5 h-5" />
          <p>You do not have permission to configure integrations.</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex gap-4 border-b border-border">
        {canGmail && (
          <button
            onClick={() => setActiveIntegration('gmail')}
            className={`pb-2 px-1 border-b-2 transition-colors ${activeIntegration === 'gmail'
              ? 'border-primary text-primary font-medium'
              : 'border-transparent text-text-secondary hover:text-text'
              }`}
          >
            Gmail
          </button>
        )}
        {canDynamics && (
          <button
            onClick={() => setActiveIntegration('dynamics')}
            className={`pb-2 px-1 border-b-2 transition-colors ${activeIntegration === 'dynamics'
              ? 'border-primary text-primary font-medium'
              : 'border-transparent text-text-secondary hover:text-text'
              }`}
          >
            Dynamics 365
          </button>
        )}
      </div>

      {activeIntegration === 'gmail' && canGmail && (
        <GmailSettings tenant={tenant} onRefresh={onRefresh} />
      )}

      {activeIntegration === 'dynamics' && canDynamics && (
        <DynamicsSettings />
      )}
    </div>
  );
}

