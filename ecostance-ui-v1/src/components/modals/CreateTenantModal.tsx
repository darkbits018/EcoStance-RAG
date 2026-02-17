import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Label } from '../ui/Label';
import { X, Mail, Shield, Building, Key } from 'lucide-react';
import { tenantsAPI } from '../../services/api';

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
      await tenantsAPI.register({
        name: formData.name,
        company: formData.company,
        email: formData.email,
        password: formData.password,
        billing_tier: formData.tier,
      });

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
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-surface border-border shadow-2xl">
        <div className="sticky top-0 bg-surface border-b border-border px-6 py-4 flex justify-between items-center z-10">
          <div>
            <h2 className="text-2xl font-bold text-text">Create New Tenant</h2>
            <p className="text-sm text-text-secondary">Provision a new organization and admin account</p>
          </div>
          <button
            onClick={handleClose}
            className="text-text-secondary hover:text-text transition-colors p-2 hover:bg-surface-hover rounded-full"
            disabled={loading}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-error/10 border border-error/20 text-error px-4 py-3 rounded-lg flex items-center gap-3">
              <X className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-text font-medium flex items-center gap-2">
                <Building className="w-4 h-4" />
                Tenant Name *
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Acme Corp"
                required
                disabled={loading}
                className="bg-background border-border text-text focus:ring-primary"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="company" className="text-text font-medium flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Company Name *
              </Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                placeholder="Acme Corporation"
                required
                disabled={loading}
                className="bg-background border-border text-text focus:ring-primary"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-text font-medium flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Admin Email *
            </Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="admin@acme.com"
              required
              disabled={loading}
              className="bg-background border-border text-text focus:ring-primary"
            />
            <p className="text-xs text-text-secondary">
              This user will receive login credentials and have full administrative access.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-text font-medium flex items-center gap-2">
              <Key className="w-4 h-4" />
              Admin Password *
            </Label>
            <div className="flex gap-2">
              <Input
                id="password"
                type="text"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Enter password or generate"
                required
                disabled={loading}
                className="flex-1 bg-background border-border text-text focus:ring-primary"
              />
              <Button
                type="button"
                variant="outline"
                onClick={generatePassword}
                disabled={loading}
                className="border-border hover:bg-surface-hover text-text"
              >
                Generate
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="tier" className="text-text font-medium">Subscription Tier *</Label>
            <select
              id="tier"
              value={formData.tier}
              onChange={(e) =>
                setFormData({ ...formData, tier: e.target.value as 'free' | 'pro' | 'enterprise' })
              }
              className="w-full px-4 py-2 border border-border rounded-lg bg-background text-text focus:ring-2 focus:ring-primary focus:outline-none"
              disabled={loading}
            >
              <option value="free">Free - 100 queries/day, 1GB storage</option>
              <option value="pro">Pro - 1,000 queries/day, 10GB storage</option>
              <option value="enterprise">Enterprise - 10,000 queries/day, 100GB storage</option>
            </select>
          </div>

          <div className="border-t border-border pt-6 mt-4">
            <h3 className="font-semibold text-text mb-2">Initial Quota Settings</h3>
            <p className="text-sm text-text-secondary">
              Default quotas will be applied based on the selected tier. You can customize these
              resource limits later from the tenant details page.
            </p>
          </div>

          <label className="flex items-center gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={formData.sendEmail}
              onChange={(e) => setFormData({ ...formData, sendEmail: e.target.checked })}
              disabled={loading}
              className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm text-text group-hover:text-primary transition-colors">
              Send welcome email with login credentials
            </span>
          </label>

          <div className="flex gap-4 pt-6 border-t border-border mt-6">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-primary hover:bg-primary/90 text-white font-semibold py-2"
            >
              {loading ? 'Creating...' : formData.sendEmail ? 'Create & Send Email' : 'Create Tenant'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={loading}
              className="flex-1 border-border text-text-secondary hover:text-text hover:bg-surface-hover"
            >
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
