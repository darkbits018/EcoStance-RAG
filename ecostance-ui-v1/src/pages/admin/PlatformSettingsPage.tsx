import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Label } from '../../components/ui/Label';

interface PlatformSettings {
  platform_name: string;
  support_email: string;
  allow_registration: boolean;
  require_email_verification: boolean;
  default_tier: 'free' | 'pro' | 'enterprise';
  jwt_expiration_minutes: number;
  max_login_attempts: number;
}

export default function PlatformSettingsPage() {
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/settings', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('access_token');
      await fetch('/api/v1/admin/settings', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
      alert('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading settings...</div>;
  }

  if (!settings) {
    return <div className="p-8">Failed to load settings</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Platform Settings</h1>
        <p className="text-gray-600 mt-1">Configure platform-wide settings</p>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">General Settings</h2>
        <div className="space-y-4">
          <div>
            <Label>Platform Name</Label>
            <Input
              value={settings.platform_name}
              onChange={(e) => setSettings({ ...settings, platform_name: e.target.value })}
            />
          </div>
          <div>
            <Label>Support Email</Label>
            <Input
              type="email"
              value={settings.support_email}
              onChange={(e) => setSettings({ ...settings, support_email: e.target.value })}
            />
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Registration Settings</h2>
        <div className="space-y-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={settings.allow_registration}
              onChange={(e) =>
                setSettings({ ...settings, allow_registration: e.target.checked })
              }
            />
            <span>Allow self-service registration</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={settings.require_email_verification}
              onChange={(e) =>
                setSettings({ ...settings, require_email_verification: e.target.checked })
              }
            />
            <span>Require email verification</span>
          </label>
          <div>
            <Label>Default tier for new tenants</Label>
            <select
              value={settings.default_tier}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  default_tier: e.target.value as 'free' | 'pro' | 'enterprise',
                })
              }
              className="w-full px-4 py-2 border rounded-md"
            >
              <option value="free">Free</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Security Settings</h2>
        <div className="space-y-4">
          <div>
            <Label>JWT Token Expiration (minutes)</Label>
            <Input
              type="number"
              value={settings.jwt_expiration_minutes}
              onChange={(e) =>
                setSettings({ ...settings, jwt_expiration_minutes: parseInt(e.target.value) })
              }
            />
          </div>
          <div>
            <Label>Max Login Attempts</Label>
            <Input
              type="number"
              value={settings.max_login_attempts}
              onChange={(e) =>
                setSettings({ ...settings, max_login_attempts: parseInt(e.target.value) })
              }
            />
          </div>
        </div>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  );
}
