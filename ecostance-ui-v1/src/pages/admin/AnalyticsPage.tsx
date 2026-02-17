import { useEffect, useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { TrendingUp, Download } from 'lucide-react';

interface AnalyticsSummary {
  total_queries: number;
  total_documents: number;
  total_storage_gb: number;
  active_tenants: number;
  avg_queries_per_tenant: number;
  avg_response_time_ms: number;
}

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [dateRange, setDateRange] = useState('30');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - parseInt(dateRange) * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0];

      const response = await fetch(
        `/api/v1/usage/summary?start_date=${startDate}&end_date=${endDate}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) {
        console.error('Failed to fetch analytics:', response.status);
        setSummary(null);
        return;
      }

      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    alert('Export functionality coming soon');
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Usage Analytics</h1>
          <p className="text-gray-600 mt-1">Platform-wide usage insights</p>
        </div>
        <div className="flex gap-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-4 py-2 border rounded-md"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading analytics...</div>
      ) : !summary ? (
        <div className="text-center py-12 text-gray-600">
          Unable to load analytics data. Please check your authentication.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Total Queries</p>
                <p className="text-3xl font-bold text-text mt-2">
                  {(summary.total_queries || 0).toLocaleString()}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-blue-400" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Total Documents</p>
                <p className="text-3xl font-bold text-text mt-2">
                  {(summary.total_documents || 0).toLocaleString()}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-purple-400" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Total Storage</p>
                <p className="text-3xl font-bold text-text mt-2">
                  {(summary.total_storage_gb || 0).toFixed(1)} GB
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-green-400" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Active Tenants</p>
                <p className="text-3xl font-bold text-text mt-2">
                  {summary.active_tenants || 0}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-indigo-400" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Avg Queries/Tenant</p>
                <p className="text-3xl font-bold text-text mt-2">
                  {(summary.avg_queries_per_tenant || 0).toFixed(0)}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-orange-400" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Avg Response Time</p>
                <p className="text-3xl font-bold text-text mt-2">
                  {summary.avg_response_time_ms || 0}ms
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-pink-400" />
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
