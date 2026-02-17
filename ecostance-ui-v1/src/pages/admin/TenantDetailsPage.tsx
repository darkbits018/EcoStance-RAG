import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Input } from '../../components/ui/Input';
import { Label } from '../../components/ui/Label';
import { Checkbox } from '../../components/ui/Checkbox';
import { ArrowLeft, Users, Database, HardDrive, Activity, Brain, Save, AlertCircle } from 'lucide-react';
import { publicAgentAPI, tenantsAPI } from '../../services/api';

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

interface AgentConfig {
  agent_type: string;
  enabled: boolean;
  allowed_tools: string[];
  branding: {
    logo_url?: string;
    primary_color: string;
    company_name: string;
  };
}

const AGENT_TYPES = [
  {
    value: 'generic',
    label: 'Generic Assistant',
    description: 'General-purpose AI assistant for any business type',
    color: 'bg-gray-500'
  },
  {
    value: 'ecommerce',
    label: 'E-commerce Agent',
    description: 'Shopping, products, and retail-focused assistant',
    color: 'bg-blue-500'
  },
  {
    value: 'ecostance',
    label: 'EcoStance Agent',
    description: 'Sustainability and environmental impact focused',
    color: 'bg-green-500'
  },
  {
    value: 'quickship',
    label: 'QuickShip Agent',
    description: 'Logistics, shipping, and supply chain focused',
    color: 'bg-purple-500'
  },
  {
    value: 'security_analyst',
    label: 'Security Analyst',
    description: 'Security, logs, and threat analysis focused',
    color: 'bg-red-500'
  }
];

const AVAILABLE_TOOLS = [
  { id: 'certificates', label: 'Carbon Certificates', description: 'Display carbon offset certificates' },
  { id: 'impact', label: 'Impact Stats', description: 'Show environmental impact metrics' },
  { id: 'shopping', label: 'Product Gallery', description: 'Display product catalogs and shopping' },
  { id: 'tracking', label: 'Order Tracking', description: 'Track shipments and logistics' },
  { id: 'analytics', label: 'Analytics Dashboard', description: 'Business analytics and reporting' },
];

export default function TenantDetailsPage() {
  const { tenantId } = useParams();
  const navigate = useNavigate();
  const [tenant, setTenant] = useState<TenantDetails | null>(null);
  const [agentConfig, setAgentConfig] = useState<AgentConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [agentLoading, setAgentLoading] = useState(false);
  const [savingAgent, setSavingAgent] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [agentError, setAgentError] = useState<string | null>(null);
  const [agentSaveStatus, setAgentSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  useEffect(() => {
    fetchTenantDetails();
    if (activeTab === 'agent') {
      fetchAgentConfig();
    }
  }, [tenantId, activeTab]);

  const fetchTenantDetails = async () => {
    if (!tenantId) return;
    try {
      const data = await tenantsAPI.getTenant(tenantId);
      setTenant(data as TenantDetails);
    } catch (error) {
      console.error('Failed to fetch tenant details:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAgentConfig = async () => {
    if (!tenantId) return;

    setAgentLoading(true);
    setAgentError(null);

    try {
      const config = await publicAgentAPI.superAdmin.getTenantAgentConfig(tenantId);
      setAgentConfig(config as AgentConfig);
    } catch (error: any) {
      console.error('Failed to fetch agent config:', error);
      setAgentError(error.message || 'Failed to load agent configuration');
      // Set default config if none exists
      setAgentConfig({
        agent_type: 'generic',
        enabled: false,
        allowed_tools: [],
        branding: {
          primary_color: '#0066CC',
          company_name: tenant?.company || 'Company'
        }
      });
    } finally {
      setAgentLoading(false);
    }
  };

  const handleSaveAgentConfig = async () => {
    if (!tenantId || !agentConfig) return;

    setSavingAgent(true);
    setAgentSaveStatus('idle');

    try {
      await publicAgentAPI.superAdmin.updateTenantAgentConfig(tenantId, agentConfig);
      setAgentSaveStatus('success');
      setTimeout(() => setAgentSaveStatus('idle'), 3000);
    } catch (error: any) {
      console.error('Failed to save agent config:', error);
      setAgentSaveStatus('error');
      setAgentError(error.message || 'Failed to save agent configuration');
    } finally {
      setSavingAgent(false);
    }
  };

  const handleSuspend = async () => {
    if (!tenantId) return;
    if (!confirm('Are you sure you want to deactivate this tenant?')) return;

    try {
      await tenantsAPI.deactivateTenant(tenantId);
      fetchTenantDetails();
    } catch (error) {
      console.error('Failed to deactivate tenant:', error);
    }
  };

  const handleReactivate = async () => {
    if (!tenantId) return;
    try {
      await tenantsAPI.activateTenant(tenantId);
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
        <Card className="p-6 bg-surface border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Total Users</p>
              <p className="text-2xl font-bold text-text mt-1">
                {tenant.stats.total_users}
              </p>
            </div>
            <Users className="w-10 h-10 text-blue-400" />
          </div>
        </Card>

        <Card className="p-6 bg-surface border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Knowledge Bases</p>
              <p className="text-2xl font-bold text-text mt-1">
                {tenant.stats.total_kbs}
              </p>
            </div>
            <Database className="w-10 h-10 text-purple-400" />
          </div>
        </Card>

        <Card className="p-6 bg-surface border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Storage Used</p>
              <p className="text-2xl font-bold text-text mt-1">
                {tenant.stats.storage_used_gb.toFixed(1)} GB
              </p>
              <p className="text-xs text-text-secondary mt-1">
                of {tenant.stats.storage_limit_gb} GB
              </p>
            </div>
            <HardDrive className="w-10 h-10 text-green-400" />
          </div>
        </Card>

        <Card className="p-6 bg-surface border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Queries (30d)</p>
              <p className="text-2xl font-bold text-text mt-1">
                {tenant.stats.queries_30d.toLocaleString()}
              </p>
              <p className="text-xs text-text-secondary mt-1">
                of {tenant.stats.query_limit_30d.toLocaleString()}
              </p>
            </div>
            <Activity className="w-10 h-10 text-indigo-400" />
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <Card className="bg-surface border-border">
        <div className="border-b border-border">
          <div className="flex gap-4 px-6 overflow-x-auto">
            {['overview', 'users', 'knowledge-bases', 'usage', 'quotas', 'agent', 'settings'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-2 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-text-secondary hover:text-text'
                  }`}
              >
                {tab === 'agent' ? (
                  <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4" />
                    AI Agent
                  </div>
                ) : (
                  tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-text-secondary mb-1">Status</p>
                  <Badge variant={tenant.status === 'active' ? 'success' : 'outline'}>
                    {tenant.status.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-text-secondary mb-1">Tier</p>
                  <Badge variant="secondary">{tenant.tier.toUpperCase()}</Badge>
                </div>
                <div>
                  <p className="text-sm text-text-secondary mb-1">Admin Email</p>
                  <p className="text-sm font-medium text-text">{tenant.admin_email}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary mb-1">Created</p>
                  <p className="text-sm font-medium text-text">
                    {new Date(tenant.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'agent' && (
            <div className="space-y-6">
              {/* Agent Configuration Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Brain className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-text">AI Agent Configuration</h3>
                    <p className="text-sm text-text-secondary">Configure the AI agent for this tenant</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {agentSaveStatus === 'success' && (
                    <span className="text-sm text-success flex items-center gap-1 bg-success/10 px-3 py-1.5 rounded-lg">
                      <AlertCircle className="h-4 w-4" />
                      Saved
                    </span>
                  )}
                  {agentSaveStatus === 'error' && (
                    <span className="text-sm text-error flex items-center gap-1 bg-error/10 px-3 py-1.5 rounded-lg">
                      <AlertCircle className="h-4 w-4" />
                      Failed
                    </span>
                  )}
                  <Button
                    onClick={handleSaveAgentConfig}
                    disabled={savingAgent || !agentConfig}
                    className="bg-primary hover:bg-primary/90"
                  >
                    {savingAgent ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        Save Configuration
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {agentError && (
                <div className="p-4 bg-error/10 border border-error/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-error mt-0.5" />
                    <div>
                      <h4 className="text-sm font-medium text-error">Configuration Error</h4>
                      <p className="text-sm text-error mt-1">{agentError}</p>
                    </div>
                  </div>
                </div>
              )}

              {agentLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                </div>
              ) : agentConfig ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Left Column - Agent Type & Status */}
                  <div className="space-y-6">
                    {/* Agent Status */}
                    <Card className="p-6 bg-surface border-border">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-text">Agent Status</h4>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={agentConfig.enabled}
                            onChange={(e) => setAgentConfig(prev => prev ? ({ ...prev, enabled: e.target.checked }) : prev)}
                            className="sr-only peer"
                          />
                          <div className="w-14 h-7 bg-surface-hover peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-text after:border-border after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-primary"></div>
                        </label>
                      </div>
                      <p className="text-sm text-text-secondary">
                        {agentConfig.enabled
                          ? 'AI Agent is active and available to users'
                          : 'AI Agent is disabled for this tenant'
                        }
                      </p>
                    </Card>

                    {/* Agent Type Selection */}
                    <Card className="p-6 bg-surface border-border">
                      <h4 className="text-lg font-semibold text-text mb-4">Agent Type</h4>
                      <div className="space-y-3">
                        {AGENT_TYPES.map((type) => (
                          <div
                            key={type.value}
                            className={`p-4 border rounded-lg cursor-pointer transition-all ${agentConfig.agent_type === type.value
                              ? 'border-primary bg-primary/5'
                              : 'border-border hover:border-primary/50 hover:bg-surface-hover'
                              }`}
                            onClick={() => setAgentConfig(prev => prev ? ({ ...prev, agent_type: type.value as any }) : prev)}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`w-3 h-3 rounded-full mt-1 ${type.color}`} />
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <h5 className="font-medium text-text">{type.label}</h5>
                                  {agentConfig.agent_type === type.value && (
                                    <Badge variant="success" className="text-xs">Selected</Badge>
                                  )}
                                </div>
                                <p className="text-sm text-text-secondary mt-1">{type.description}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </Card>
                  </div>

                  {/* Right Column - Tools & Branding */}
                  <div className="space-y-6">
                    {/* Available Tools */}
                    <Card className="p-6 bg-surface border-border">
                      <h4 className="text-lg font-semibold text-text mb-4">Available Tools</h4>
                      <div className="space-y-3">
                        {AVAILABLE_TOOLS.map((tool) => (
                          <div key={tool.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-surface-hover transition-colors">
                            <div className="flex-1">
                              <p className="font-medium text-text">{tool.label}</p>
                              <p className="text-sm text-text-secondary">{tool.description}</p>
                            </div>
                            <Checkbox
                              checked={agentConfig.allowed_tools.includes(tool.id)}
                              onChange={(e) => {
                                const tools = e.target.checked
                                  ? [...agentConfig.allowed_tools, tool.id]
                                  : agentConfig.allowed_tools.filter(t => t !== tool.id);
                                setAgentConfig(prev => prev ? ({ ...prev, allowed_tools: tools }) : prev);
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    </Card>

                    {/* Branding */}
                    <Card className="p-6 bg-surface border-border">
                      <h4 className="text-lg font-semibold text-text mb-4">Branding</h4>
                      <div className="space-y-4">
                        <div>
                          <Label className="text-sm font-medium text-text">Company Name</Label>
                          <Input
                            value={agentConfig.branding.company_name}
                            onChange={(e) => setAgentConfig(prev => prev ? ({
                              ...prev,
                              branding: { ...prev.branding, company_name: e.target.value }
                            }) : prev)}
                            placeholder="Company Name"
                            className="mt-1.5"
                          />
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-text">Logo URL</Label>
                          <Input
                            value={agentConfig.branding.logo_url || ''}
                            onChange={(e) => setAgentConfig(prev => prev ? ({
                              ...prev,
                              branding: { ...prev.branding, logo_url: e.target.value }
                            }) : prev)}
                            placeholder="https://example.com/logo.png"
                            className="mt-1.5"
                          />
                          <p className="text-xs text-text-secondary mt-1">Optional - leave empty for default</p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-text">Primary Color</Label>
                          <div className="flex gap-2 mt-1.5">
                            <Input
                              type="color"
                              value={agentConfig.branding.primary_color}
                              onChange={(e) => setAgentConfig(prev => prev ? ({
                                ...prev,
                                branding: { ...prev.branding, primary_color: e.target.value }
                              }) : prev)}
                              className="w-16 h-10 p-1 cursor-pointer"
                            />
                            <Input
                              value={agentConfig.branding.primary_color}
                              onChange={(e) => setAgentConfig(prev => prev ? ({
                                ...prev,
                                branding: { ...prev.branding, primary_color: e.target.value }
                              }) : prev)}
                              placeholder="#0066CC"
                              className="flex-1"
                            />
                          </div>
                        </div>
                      </div>
                    </Card>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Brain className="w-12 h-12 text-text-secondary mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-text mb-2">No Agent Configuration</h3>
                  <p className="text-text-secondary">Failed to load agent configuration for this tenant.</p>
                </div>
              )}
            </div>
          )}

          {activeTab !== 'overview' && activeTab !== 'agent' && (
            <p className="text-text-secondary text-center py-8">
              {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} content coming soon
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}
