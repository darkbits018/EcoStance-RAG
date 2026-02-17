import { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Trash2, Database, Archive, Zap } from 'lucide-react';

interface CleanupTask {
  id: string;
  name: string;
  description: string;
  icon: any;
  lastRun: string;
  itemsToClean: string;
  endpoint: string;
}

export default function MaintenancePage() {
  const [loading, setLoading] = useState<string | null>(null);

  const tasks: CleanupTask[] = [
    {
      id: 'sessions',
      name: 'Cleanup Old Sessions',
      description: 'Remove expired user sessions',
      icon: Trash2,
      lastRun: '2 hours ago',
      itemsToClean: '~150 sessions',
      endpoint: '/api/v1/admin/cleanup/sessions',
    },
    {
      id: 'temp-files',
      name: 'Cleanup Temp Files',
      description: 'Remove temporary uploaded files',
      icon: Trash2,
      lastRun: '1 day ago',
      itemsToClean: '~45 files (2.3 GB)',
      endpoint: '/api/v1/admin/cleanup/temp-files',
    },
    {
      id: 'audit-logs',
      name: 'Archive Audit Logs',
      description: 'Archive old audit logs to cold storage',
      icon: Archive,
      lastRun: '30 days ago',
      itemsToClean: '~50,000 logs',
      endpoint: '/api/v1/admin/cleanup/audit-logs',
    },
    {
      id: 'optimize-db',
      name: 'Optimize Database',
      description: 'Run VACUUM and ANALYZE on PostgreSQL',
      icon: Database,
      lastRun: '7 days ago',
      itemsToClean: 'Est. 10-15 minutes',
      endpoint: '/api/v1/admin/cleanup/optimize-db',
    },
  ];

  const runCleanup = async (task: CleanupTask) => {
    if (!confirm(`Are you sure you want to run: ${task.name}?`)) return;

    setLoading(task.id);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(task.endpoint, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        alert(`${task.name} completed successfully`);
      } else {
        alert(`${task.name} failed`);
      }
    } catch (error) {
      console.error('Cleanup failed:', error);
      alert('Cleanup failed');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Cleanup & Maintenance</h1>
        <p className="text-gray-600 mt-1">Run cleanup tasks and maintain system health</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tasks.map((task) => {
          const Icon = task.icon;
          return (
            <Card key={task.id} className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-text">{task.name}</h3>
                  <p className="text-sm text-text-secondary mt-1">{task.description}</p>
                  <div className="mt-3 space-y-1 text-sm">
                    <p className="text-text-secondary">
                      <span className="font-medium text-text">Last run:</span> {task.lastRun}
                    </p>
                    <p className="text-text-secondary">
                      <span className="font-medium text-text">Items to clean:</span> {task.itemsToClean}
                    </p>
                  </div>
                  <Button
                    onClick={() => runCleanup(task)}
                    disabled={loading === task.id}
                    className="mt-4"
                    size="sm"
                  >
                    {loading === task.id ? 'Running...' : 'Run Now'}
                  </Button>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-bold text-text mb-4">Run All Cleanup Tasks</h2>
        <p className="text-text-secondary mb-4">
          Execute all cleanup tasks in sequence. This may take several minutes.
        </p>
        <Button
          variant="destructive"
          onClick={async () => {
            if (!confirm('Run all cleanup tasks? This may take several minutes.')) return;
            setLoading('all');
            try {
              const token = localStorage.getItem('access_token');
              await fetch('/api/v1/admin/cleanup/all', {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
              });
              alert('All cleanup tasks completed');
            } catch (error) {
              alert('Cleanup failed');
            } finally {
              setLoading(null);
            }
          }}
          disabled={loading === 'all'}
        >
          <Zap className="w-4 h-4 mr-2" />
          {loading === 'all' ? 'Running All Tasks...' : 'Run All Tasks'}
        </Button>
      </Card>
    </div>
  );
}
