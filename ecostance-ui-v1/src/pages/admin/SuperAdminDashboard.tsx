import React, { useEffect, useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Building, Users, Search, Heart, TrendingUp, AlertCircle } from 'lucide-react';
import { Button } from '../../components/ui/Button';

interface DashboardSummary {
  total_tenants: number;
  total_users: number;
  total_queries_today: number;
  system_health: 'healthy' | 'warning' | 'critical';
  uptime_percentage: number;
  tenant_growth: number;
  active_users_30d: number;
  queries_yesterday: number;
}

interface ActivityEvent {
  id: string;
  timestamp: string;
  event_type: string;
  tenant_name: string;
  details: string;
}

export default function SuperAdminDashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [activities, setActivities] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/dashboard/summary', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (!response.ok) {
        console.warn('Dashboard API not available, using mock data');
        // Use mock data for development
        setSummary({
          total_tenants: 0,
          total_users: 0,
          total_queries_today: 0,
          system_health: 'healthy',
          uptime_percentage: 99.9,
          tenant_growth: 0,
          active_users_30d: 0,
          queries_yesterday: 0,
        });
        setActivities([]);
        setLoading(false);
        return;
      }
      
      const data = await response.json();
      setSummary(data);
      setActivities(data.recent_events || []);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      // Set empty data on error
      setSummary({
        total_tenants: 0,
        total_users: 0,
        total_queries_today: 0,
        system_health: 'healthy',
        uptime_percentage: 99.9,
        tenant_growth: 0,
        active_users_30d: 0,
        queries_yesterday: 0,
      });
      setActivities([]);
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-600 bg-green-50';
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      case 'critical': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Platform overview and metrics</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={fetchDashboardData}>
            Refresh
          </Button>
          <Button onClick={() => window.location.href = '/admin/tenants/create'}>
            Create New Tenant
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Tenants</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {summary?.total_tenants || 0}
              </p>
              <p className="text-sm text-green-600 mt-2 flex items-center">
                <TrendingUp className="w-4 h-4 mr-1" />
                +{summary?.tenant_growth || 0}% vs last month
              </p>
            </div>
            <Building className="w-12 h-12 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Users</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {summary?.total_users || 0}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                {summary?.active_users_30d || 0} active (30d)
              </p>
            </div>
            <Users className="w-12 h-12 text-purple-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Queries Today</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {summary?.total_queries_today || 0}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                vs {summary?.queries_yesterday || 0} yesterday
              </p>
            </div>
            <Search className="w-12 h-12 text-indigo-600" />
          </div>
        </Card>

        <Card className={`p-6 ${summary ? getHealthColor(summary.system_health) : ''}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">System Health</p>
              <p className="text-3xl font-bold mt-2 capitalize">
                {summary?.system_health || 'Unknown'}
              </p>
              <p className="text-sm mt-2">
                {summary?.uptime_percentage || 0}% uptime
              </p>
            </div>
            <Heart className="w-12 h-12" />
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {activities.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No recent activity</p>
          ) : (
            activities.map((event) => (
              <div key={event.id} className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded">
                <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{event.event_type}</p>
                  <p className="text-sm text-gray-600">{event.tenant_name} - {event.details}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(event.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button variant="outline" className="h-20" onClick={() => window.location.href = '/admin/tenants'}>
            View All Tenants
          </Button>
          <Button variant="outline" className="h-20" onClick={() => window.location.href = '/admin/system'}>
            System Health
          </Button>
          <Button variant="outline" className="h-20" onClick={() => window.location.href = '/admin/settings'}>
            Platform Settings
          </Button>
          <Button variant="outline" className="h-20" onClick={() => window.location.href = '/admin/maintenance'}>
            Run Cleanup
          </Button>
        </div>
      </Card>
    </div>
  );
}
