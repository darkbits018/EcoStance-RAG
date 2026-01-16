import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { ArrowLeft, Users, Database, HardDrive, Activity } from 'lucide-react';

interface TenantDetails {
  id: string;
  name: string;
  company: string;
  status: 'active' | 'suspended' | 'inactive';
  tier: 'free' | 'pro' | 'enterprise';
  admin_email: string;
  created_at: string;
  last_activity: string;
  stats: {
    total_users: number;
    total_kbs: number;
    total_documents: number;
    storage_used_gb: number;
    storage_limit_gb: number;
    queries_30d: number;
    query_limit_30d: number;
  };
}

export default function TenantDetailsPage() {
  const { tenantId } = useParams();
  const navigate = useNavigate();
  const [tenant, setTenant] = useState<TenantDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchTenantDetails();
  }, [tenantId]);

  const fetchTenantDetails = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/tenants/${tenantId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setTenant(data);
    } catch (error) {
      console.error('Failed to fetch tenant details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuspend = async () => {
    if (!confirm('Are you sure you want to suspend this tenant?')) return;
    
    try {
      const token = localStorage.getItem('access_token');
      await fetch(`/api/v1/admin/tenants/${tenantId}/suspend`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      fetchTenantDetails();
    } catch (error) {
      console.error('Failed to suspend tenant:', error);
    }
  };

  const handleReactivate = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await fetch(`/api/v1/admin/tenants/${tenantId}/reactivate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      fetchTenantDetails();
    } catch (error) {
      console.error('Failed to reactivate tenant:', error);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!tenant) {
    return <div className="p-8">Tenant not found</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => navigate('/admin/tenants')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">{tenant.name}</h1>
          <p className="text-gray-600">{tenant.company}</p>
        </div>
        <div className="flex gap-2">
          {tenant.status === 'active' ? (
            <Button variant="destructive" onClick={handleSuspend}>
              Suspend Tenant
            </Button>
          ) : (
            <Button onClick={handleReactivate}>
              Reactivate Tenant
            </Button>
          )}
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {tenant.stats.total_users}
              </p>
            </div>
            <Users className="w-10 h-10 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Knowledge Bases</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {tenant.stats.total_kbs}
              </p>
            </div>
            <Database className="w-10 h-10 text-purple-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {tenant.stats.storage_used_gb.toFixed(1)} GB
              </p>
              <p className="text-xs text-gray-500 mt-1">
                of {tenant.stats.storage_limit_gb} GB
              </p>
            </div>
            <HardDrive className="w-10 h-10 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Queries (30d)</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {tenant.stats.queries_30d.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                of {tenant.stats.query_limit_30d.toLocaleString()}
              </p>
            </div>
            <Activity className="w-10 h-10 text-indigo-600" />
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <Card>
        <div className="border-b">
          <div className="flex gap-4 px-6">
            {['overview', 'users', 'knowledge-bases', 'usage', 'quotas', 'settings'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  <Badge variant={tenant.status === 'active' ? 'success' : 'warning'}>
                    {tenant.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Tier</p>
                  <Badge>{tenant.tier.toUpperCase()}</Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Admin Email</p>
                  <p className="text-sm font-medium">{tenant.admin_email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Created</p>
                  <p className="text-sm font-medium">
                    {new Date(tenant.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          )}
          {activeTab !== 'overview' && (
            <p className="text-gray-500 text-center py-8">
              {tab.charAt(0).toUpperCase() + tab.slice(1)} content coming soon
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}
