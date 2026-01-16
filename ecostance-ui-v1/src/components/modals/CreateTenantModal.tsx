import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Label } from '../ui/Label';
import { X } from 'lucide-react';

interface CreateTenantModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateTenantModal({ isOpen, onClose, onSuccess }: CreateTenantModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    email: '',
    password: '',
    tier: 'free' as 'free' | 'pro' | 'enterprise',
    sendEmail: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/tenants/register', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          company: formData.company,
          email: formData.email,
          password: formData.password,
          tier: formData.tier,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create tenant');
      }

      if (formData.sendEmail) {
        // Optionally send welcome email
        // await sendWelcomeEmail(formData.email);
      }

      onSuccess();
      handleClose();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      name: '',
      company: '',
      email: '',
      password: '',
      tier: 'free',
      sendEmail: true,
    });
    setError('');
    onClose();
  };

  const generatePassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 16; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setFormData({ ...formData, password });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Create New Tenant</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={loading}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="name">Tenant Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Acme Corp"
                required
                disabled={loading}
              />
            </div>

            <div>
              <Label htmlFor="company">Company Name *</Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                placeholder="Acme Corporation"
                required
                disabled={loading}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="email">Admin Email *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="admin@acme.com"
              required
              disabled={loading}
            />
            <p className="text-sm text-gray-500 mt-1">
              This user will receive login credentials
            </p>
          </div>

          <div>
            <Label htmlFor="password">Admin Password *</Label>
            <div className="flex gap-2">
              <Input
                id="password"
                type="text"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Enter password or generate"
                required
                disabled={loading}
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                onClick={generatePassword}
                disabled={loading}
              >
                Generate
              </Button>
            </div>
          </div>

          <div>
            <Label htmlFor="tier">Tier *</Label>
            <select
              id="tier"
              value={formData.tier}
              onChange={(e) =>
                setFormData({ ...formData, tier: e.target.value as 'free' | 'pro' | 'enterprise' })
              }
              className="w-full px-4 py-2 border rounded-md"
              disabled={loading}
            >
              <option value="free">Free - 100 queries/day, 1GB storage</option>
              <option value="pro">Pro - 1,000 queries/day, 10GB storage</option>
              <option value="enterprise">Enterprise - 10,000 queries/day, 100GB storage</option>
            </select>
          </div>

          <div className="border-t pt-4">
            <h3 className="font-semibold text-gray-900 mb-3">Initial Quota Settings</h3>
            <p className="text-sm text-gray-600">
              Default quotas will be applied based on the selected tier. You can customize these
              later from the tenant details page.
            </p>
          </div>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.sendEmail}
              onChange={(e) => setFormData({ ...formData, sendEmail: e.target.checked })}
              disabled={loading}
            />
            <span className="text-sm text-gray-700">
              Send welcome email with login credentials
            </span>
          </label>

          <div className="flex gap-3 pt-4 border-t">
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Creating...' : formData.sendEmail ? 'Create & Send Email' : 'Create Tenant'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={loading}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
