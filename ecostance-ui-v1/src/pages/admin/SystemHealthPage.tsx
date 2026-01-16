import React, { useEffect, useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Server, Database, Cpu, AlertTriangle } from 'lucide-react';

interface SystemHealth {
  api_status: 'online' | 'offline';
  api_uptime: number;
  api_response_time: number;
  api_requests_per_min: number;
  database_status: 'online' | 'offline';
  database_connections: number;
  database_max_connections: number;
  database_query_time: number;
  database_storage_gb: number;
  database_storage_limit_gb: number;
  qdrant_status: 'online' | 'offline';
  qdrant_collections: number;
  qdrant_vectors: number;
  qdrant_memory_gb: number;
  qdrant_memory_limit_gb: number;
  background_jobs_status: 'running' | 'stopped';
  active_jobs: number;
  failed_jobs_24h: number;
}

export default function SystemHealthPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemHealth();
    const interval = setInterval(fetchSystemHealth, 10000); // Update every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchSystemHealth = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/health/system', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setHealth(data);
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    return (
      <Badge variant={status === 'online' || status === 'running' ? 'success' : 'destructive'}>
        {status.toUpperCase()}
      </Badge>
    );
  };

  if (loading) {
    return <div className="p-8">Loading system health...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">System Health & Monitoring</h1>
        <p className="text-gray-600 mt-1">Monitor platform infrastructure and performance</p>
      </div>

      {/* Service Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Server className="w-8 h-8 text-blue-600" />
              <h2 className="text-xl font-bold">API Server</h2>
            </div>
            {getStatusBadge(health?.api_status || 'offline')}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Uptime</span>
              <span className="font-medium">{health?.api_uptime.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Response Time</span>
              <span className="font-medium">{health?.api_response_time}ms avg</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Requests/min</span>
              <span className="font-medium">{health?.api_requests_per_min.toLocaleString()}</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Database className="w-8 h-8 text-purple-600" />
              <h2 className="text-xl font-bold">PostgreSQL</h2>
            </div>
            {getStatusBadge(health?.database_status || 'offline')}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Connections</span>
              <span className="font-medium">
                {health?.database_connections}/{health?.database_max_connections}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Query Time</span>
              <span className="font-medium">{health?.database_query_time}ms avg</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Storage</span>
              <span className="font-medium">
                {health?.database_storage_gb.toFixed(1)}/{health?.database_storage_limit_gb} GB
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Cpu className="w-8 h-8 text-green-600" />
              <h2 className="text-xl font-bold">Qdrant</h2>
            </div>
            {getStatusBadge(health?.qdrant_status || 'offline')}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Collections</span>
              <span className="font-medium">{health?.qdrant_collections}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Vectors</span>
              <span className="font-medium">{(health?.qdrant_vectors || 0).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Memory</span>
              <span className="font-medium">
                {health?.qdrant_memory_gb.toFixed(1)}/{health?.qdrant_memory_limit_gb} GB
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-8 h-8 text-orange-600" />
              <h2 className="text-xl font-bold">Background Jobs</h2>
            </div>
            {getStatusBadge(health?.background_jobs_status || 'stopped')}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Active Jobs</span>
              <span className="font-medium">{health?.active_jobs}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Failed (24h)</span>
              <span className="font-medium text-red-600">{health?.failed_jobs_24h}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
