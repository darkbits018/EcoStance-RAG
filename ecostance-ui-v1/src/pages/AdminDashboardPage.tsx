import { useState, useEffect } from 'react';
import { tenantsAPI, metricsAPI } from '../services/api';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Shield, Users, Activity, TrendingUp, Search, Eye, Trash2, CheckCircle, XCircle } from 'lucide-react';

interface Tenant {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  billing_tier: string;
  billing_status: string;
  created_at: string;
}

interface TenantMetrics {
  tenant_name: string;
  tenant_tier: string;
  metrics: Array<{
    period_start: string;
    storage: { gb: number; document_count: number };
    queries: { total: number; success_rate: number };
    api: { total_calls: number; success_rate: number };
  }>;
}

export default function AdminDashboardPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  const [tenantMetrics, setTenantMetrics] = useState<Record<string, TenantMetrics>>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadTenants();
    loadSystemMetrics();
  }, []);

  const loadTenants = async () => {
    try {
      const data = await tenantsAPI.listTenants(0, 100) as Tenant[];
      setTenants(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load tenants');
    }
  };

  const loadSystemMetrics = async () => {
    try {
      const data = await metricsAPI.getAllTenantMetrics('daily', 7) as { data: Record<string, TenantMetrics> };
      setTenantMetrics(data.data);
    } catch (err: any) {
      console.error('Failed to load metrics:', err);
    }
  };

  const handleActivateTenant = async (tenantId: string) => {
    try {
      await tenantsAPI.activateTenant(tenantId);
      await loadTenants();
      setSuccess('Tenant activated successfully');
    } catch (err: any) {
      setError(err.message || 'Failed to activate tenant');
    }
  };

  const handleDeactivateTenant = async (tenantId: string) => {
    if (!confirm('Deactivate this tenant? They will lose access immediately.')) return;
    try {
      await tenantsAPI.deactivateTenant(tenantId);
      await loadTenants();
      setSuccess('Tenant deactivated successfully');
    } catch (err: any) {
      setError(err.message || 'Failed to deactivate tenant');
    }
  };

  const handleDeleteTenant = async (tenantId: string) => {
    if (!confirm('Delete this tenant? This action cannot be undone.')) return;
    try {
      await tenantsAPI.deleteTenant(tenantId, false);
      await loadTenants();
      setSuccess('Tenant deleted successfully');
    } catch (err: any) {
      setError(err.message || 'Failed to delete tenant');
    }
  };

  const filteredTenants = tenants.filter(
    (t) =>
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const systemStats = {
    totalTenants: tenants.length,
    activeTenants: tenants.filter((t) => t.is_active).length,
    inactiveTenants: tenants.filter((t) => !t.is_active).length,
    tierBreakdown: tenants.reduce((acc, t) => {
      acc[t.billing_tier] = (acc[t.billing_tier] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text flex items-center gap-2">
              <Shield className="w-6 h-6 text-error" />
              Admin Dashboard
              <span className="ml-2 px-2 py-1 bg-error/10 text-error text-xs font-semibold rounded border border-error/20">
                SUPER ADMIN ONLY
              </span>
            </h1>
            <p className="text-text-secondary mt-1">Manage tenants and monitor system health</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-error/10 border border-error/20 rounded-lg">
          <p className="text-error">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-success/10 border border-success/20 rounded-lg">
          <p className="text-success">{success}</p>
        </div>
      )}

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="p-4 bg-surface border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Total Tenants</p>
              <p className="text-2xl font-bold text-text">{systemStats.totalTenants}</p>
            </div>
            <Users className="w-8 h-8 text-primary" />
          </div>
        </Card>

        <Card className="p-4 bg-surface border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Active</p>
              <p className="text-2xl font-bold text-success">{systemStats.activeTenants}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-success" />
          </div>
        </Card>

        <Card className="p-4 bg-surface border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Inactive</p>
              <p className="text-2xl font-bold text-error">{systemStats.inactiveTenants}</p>
            </div>
            <XCircle className="w-8 h-8 text-error" />
          </div>
        </Card>

        <Card className="p-4 bg-surface border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">System Health</p>
              <p className="text-2xl font-bold text-success">Good</p>
            </div>
            <Activity className="w-8 h-8 text-success" />
          </div>
        </Card>
      </div>

      {/* Tier Breakdown */}
      <Card className="p-6 mb-6 bg-surface border-border">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-text">
          <TrendingUp className="w-5 h-5 text-primary" />
          Billing Tier Distribution
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(systemStats.tierBreakdown).map(([tier, count]) => (
            <div key={tier} className="text-center p-4 bg-background rounded-lg border border-border">
              <p className="text-2xl font-bold text-text">{count}</p>
              <p className="text-sm text-text-secondary capitalize">{tier}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Tenant Management */}
      <Card className="p-6 bg-surface border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-text">Tenant Management</h2>
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary" />
            <input
              type="text"
              placeholder="Search tenants..."
              className="pl-10 pr-4 py-2 bg-background border border-border rounded-lg w-64 text-text placeholder:text-text-secondary focus:border-primary focus:outline-none"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-background">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-text">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text">Email</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text">Tier</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text">Created</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredTenants.map((tenant) => (
                <tr key={tenant.id} className="hover:bg-surface-hover">
                  <td className="px-4 py-3 text-sm font-medium text-text">{tenant.name}</td>
                  <td className="px-4 py-3 text-sm text-text-secondary">{tenant.email}</td>
                  <td className="px-4 py-3 text-sm">
                    <span className="px-2 py-1 bg-primary/10 text-primary rounded text-xs capitalize border border-primary/20">
                      {tenant.billing_tier}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span
                      className={`px-2 py-1 rounded text-xs border ${
                        tenant.is_active
                          ? 'bg-success/10 text-success border-success/20'
                          : 'bg-error/10 text-error border-error/20'
                      }`}
                    >
                      {tenant.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary">{formatDate(tenant.created_at)}</td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setSelectedTenant(tenant)}
                        className="text-primary hover:text-primary/80"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      {tenant.is_active ? (
                        <button
                          onClick={() => handleDeactivateTenant(tenant.id)}
                          className="text-warning hover:text-warning/80"
                          title="Deactivate"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivateTenant(tenant.id)}
                          className="text-success hover:text-success/80"
                          title="Activate"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteTenant(tenant.id)}
                        className="text-error hover:text-error/80"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredTenants.length === 0 && (
            <p className="text-center text-text-secondary py-8">No tenants found</p>
          )}
        </div>
      </Card>

      {/* Tenant Details Modal */}
      {selectedTenant && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <Card className="p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto bg-surface border-border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-text">Tenant Details</h2>
              <button
                onClick={() => setSelectedTenant(null)}
                className="text-text-secondary hover:text-text text-2xl"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Tenant ID</label>
                <div className="px-3 py-2 bg-background rounded border border-border text-sm text-text">{selectedTenant.id}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Name</label>
                <div className="px-3 py-2 bg-background rounded border border-border text-sm text-text">{selectedTenant.name}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Email</label>
                <div className="px-3 py-2 bg-background rounded border border-border text-sm text-text">{selectedTenant.email}</div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">Billing Tier</label>
                  <div className="px-3 py-2 bg-background rounded border border-border text-sm capitalize text-text">
                    {selectedTenant.billing_tier}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">Status</label>
                  <div className="px-3 py-2 bg-background rounded border border-border text-sm capitalize text-text">
                    {selectedTenant.billing_status}
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Created At</label>
                <div className="px-3 py-2 bg-background rounded border border-border text-sm text-text">
                  {formatDate(selectedTenant.created_at)}
                </div>
              </div>

              {tenantMetrics[selectedTenant.id] && (
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">Recent Activity</label>
                  <div className="space-y-2">
                    {tenantMetrics[selectedTenant.id].metrics.slice(0, 3).map((metric, idx) => (
                      <div key={idx} className="p-3 bg-background rounded border border-border text-sm">
                        <div className="flex justify-between mb-1">
                          <span className="text-text-secondary">Storage:</span>
                          <span className="font-medium text-text">{metric.storage.gb.toFixed(2)} GB</span>
                        </div>
                        <div className="flex justify-between mb-1">
                          <span className="text-text-secondary">Queries:</span>
                          <span className="font-medium text-text">{metric.queries.total}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-secondary">API Calls:</span>
                          <span className="font-medium text-text">{metric.api.total_calls}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 flex gap-2">
              <Button onClick={() => setSelectedTenant(null)}>Close</Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
