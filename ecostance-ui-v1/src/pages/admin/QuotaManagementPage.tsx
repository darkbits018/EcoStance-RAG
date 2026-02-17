import { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Label } from '../../components/ui/Label';

interface QuotaTemplate {
  tier: 'free' | 'pro' | 'enterprise';
  max_queries_per_day: number;
  max_queries_per_month: number;
  max_documents: number;
  max_storage_gb: number;
  max_knowledge_bases: number;
  max_concurrent_queries: number;
}

export default function QuotaManagementPage() {
  const [templates, setTemplates] = useState<QuotaTemplate[]>([]);
  const [editingTier, setEditingTier] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<QuotaTemplate | null>(null);

  useEffect(() => {
    fetchQuotaTemplates();
  }, []);

  const fetchQuotaTemplates = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/quotas/templates', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to fetch quota templates:', error);
    }
  };

  const handleEdit = (template: QuotaTemplate) => {
    setEditingTier(template.tier);
    setEditForm({ ...template });
  };

  const handleSave = async () => {
    if (!editForm) return;

    try {
      const token = localStorage.getItem('access_token');
      await fetch(`/api/v1/admin/quotas/templates/${editForm.tier}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editForm),
      });
      setEditingTier(null);
      setEditForm(null);
      fetchQuotaTemplates();
    } catch (error) {
      console.error('Failed to update quota template:', error);
    }
  };

  const getTierColor = (tier: string) => {
    const colors: Record<string, string> = {
      free: 'border-gray-500',
      pro: 'border-blue-500',
      enterprise: 'border-purple-500',
    };
    return colors[tier] || 'border-gray-500';
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Quota Management</h1>
        <p className="text-gray-600 mt-1">Manage resource quotas and limits</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {templates.map((template) => (
          <Card key={template.tier} className={`p-6 border-2 ${getTierColor(template.tier)}`}>
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold capitalize text-text">{template.tier} Tier</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleEdit(template)}
                className="text-text border-border hover:bg-surface-hover"
              >
                Edit
              </Button>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-sm text-text-secondary">Queries per day</p>
                <p className="text-lg font-semibold text-text">{template.max_queries_per_day.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Queries per month</p>
                <p className="text-lg font-semibold text-text">{template.max_queries_per_month.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Max documents</p>
                <p className="text-lg font-semibold text-text">
                  {template.max_documents === -1 ? 'Unlimited' : template.max_documents.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Max storage</p>
                <p className="text-lg font-semibold text-text">{template.max_storage_gb} GB</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Max knowledge bases</p>
                <p className="text-lg font-semibold text-text">
                  {template.max_knowledge_bases === -1 ? 'Unlimited' : template.max_knowledge_bases}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Concurrent queries</p>
                <p className="text-lg font-semibold text-text">{template.max_concurrent_queries}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Edit Modal */}
      {editingTier && editForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md p-6 m-4 bg-surface border-border">
            <h2 className="text-2xl font-bold mb-4 capitalize text-text">Edit {editForm.tier} Tier</h2>

            <div className="space-y-4">
              <div>
                <Label className="text-text-secondary">Queries per day</Label>
                <Input
                  type="number"
                  value={editForm.max_queries_per_day}
                  onChange={(e) => setEditForm({ ...editForm, max_queries_per_day: parseInt(e.target.value) })}
                  className="bg-background text-text border-border"
                />
              </div>
              <div>
                <Label className="text-text-secondary">Queries per month</Label>
                <Input
                  type="number"
                  value={editForm.max_queries_per_month}
                  onChange={(e) => setEditForm({ ...editForm, max_queries_per_month: parseInt(e.target.value) })}
                  className="bg-background text-text border-border"
                />
              </div>
              <div>
                <Label className="text-text-secondary">Max documents (-1 for unlimited)</Label>
                <Input
                  type="number"
                  value={editForm.max_documents}
                  onChange={(e) => setEditForm({ ...editForm, max_documents: parseInt(e.target.value) })}
                  className="bg-background text-text border-border"
                />
              </div>
              <div>
                <Label className="text-text-secondary">Max storage (GB)</Label>
                <Input
                  type="number"
                  value={editForm.max_storage_gb}
                  onChange={(e) => setEditForm({ ...editForm, max_storage_gb: parseInt(e.target.value) })}
                  className="bg-background text-text border-border"
                />
              </div>
              <div>
                <Label className="text-text-secondary">Max knowledge bases (-1 for unlimited)</Label>
                <Input
                  type="number"
                  value={editForm.max_knowledge_bases}
                  onChange={(e) => setEditForm({ ...editForm, max_knowledge_bases: parseInt(e.target.value) })}
                  className="bg-background text-text border-border"
                />
              </div>
              <div>
                <Label className="text-text-secondary">Max concurrent queries</Label>
                <Input
                  type="number"
                  value={editForm.max_concurrent_queries}
                  onChange={(e) => setEditForm({ ...editForm, max_concurrent_queries: parseInt(e.target.value) })}
                  className="bg-background text-text border-border"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <Button onClick={handleSave} className="flex-1">
                Save Changes
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setEditingTier(null);
                  setEditForm(null);
                }}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
