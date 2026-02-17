import { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import {
    Building,
    Mail,
    Calendar,
    Shield,
    AlertCircle,
    Trash2,
    PauseCircle,
    PlayCircle,
    Clock,
    ExternalLink,
    X,
    CreditCard,
    Check
} from 'lucide-react';
import { tenantsAPI, adminAPI } from '../../services/api';

interface Tenant {
    id: string;
    name: string;
    company: string;
    status: 'active' | 'suspended' | 'inactive';
    tier: 'free' | 'pro' | 'enterprise' | 'starter' | 'professional'; // Added 'starter' and 'professional'
    email: string;
    created_at: string;
    user_count: number;
    kb_count: number;
    storage_gb: number;
}

interface ManageTenantModalProps {
    isOpen: boolean;
    onClose: () => void;
    tenant: Tenant | null;
    onUpdate: () => void;
}

export default function ManageTenantModal({ isOpen, onClose, tenant, onUpdate }: ManageTenantModalProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [newTier, setNewTier] = useState<string>(tenant?.tier || 'free');

    if (!isOpen || !tenant) return null;

    const handleStatusToggle = async () => {
        const isActivating = tenant.status !== 'active';
        const action = isActivating ? 'reactivate' : 'suspend';

        if (!confirm(`Are you sure you want to ${action} this tenant?`)) return;

        setLoading(true);
        setError(null);
        try {
            if (isActivating) {
                await tenantsAPI.activateTenant(tenant.id);
            } else {
                await tenantsAPI.deactivateTenant(tenant.id);
            }
            onUpdate();
            onClose();
        } catch (err: any) {
            setError(err.message || `Failed to ${action} tenant`);
        } finally {
            setLoading(false);
        }
    };

    const handleTierChange = async () => {
        if (newTier === tenant.tier) return; // No change

        if (!confirm(`Are you sure you want to change the tier to ${newTier.toUpperCase()} for this tenant?`)) return;

        setLoading(true);
        setError(null);
        try {
            await adminAPI.updateTenantTier(tenant.id, newTier);
            onUpdate();
            onClose();
        } catch (err: any) {
            setError(err.message || `Failed to update tenant tier to ${newTier}`);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!confirm('CRITICAL ACTION: This will completely delete the tenant and all their data. This cannot be undone. Are you absolutely sure? Type "DELETE" to confirm.')) return;

        const confirmation = prompt('Please type DELETE to confirm:');
        if (confirmation !== 'DELETE') return;

        setLoading(true);
        setError(null);
        try {
            await tenantsAPI.deleteTenant(tenant.id, true);
            onUpdate();
            onClose();
        } catch (err: any) {
            setError(err.message || 'Failed to delete tenant');
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'active':
                return <Badge variant="success" className="flex items-center gap-1"><PlayCircle className="w-3 h-3" /> ACTIVE</Badge>;
            case 'suspended':
                return <Badge variant="destructive" className="flex items-center gap-1"><PauseCircle className="w-3 h-3" /> SUSPENDED</Badge>;
            default:
                return <Badge variant="outline" className="flex items-center gap-1"><Clock className="w-3 h-3" /> {status.toUpperCase()}</Badge>;
        }
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-surface border-border shadow-2xl">
                <div className="sticky top-0 bg-surface border-b border-border px-6 py-4 flex justify-between items-center z-10">
                    <div>
                        <h2 className="text-2xl font-bold text-text">Manage Tenant</h2>
                        <p className="text-sm text-text-secondary">Viewing and managing organization status</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-text-secondary hover:text-text transition-colors p-2 hover:bg-surface-hover rounded-full"
                        disabled={loading}
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {error && (
                        <div className="p-4 bg-error/10 border border-error/20 rounded-lg flex items-center gap-3 text-error">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            <p className="text-sm font-medium">{error}</p>
                        </div>
                    )}

                    {/* Basic Info */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <div>
                                <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Tenant Name</label>
                                <div className="mt-1 flex items-center gap-2 text-text">
                                    <Shield className="w-4 h-4 text-primary" />
                                    <span className="font-semibold">{tenant.name}</span>
                                </div>
                            </div>

                            <div>
                                <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Company</label>
                                <div className="mt-1 flex items-center gap-2 text-text">
                                    <Building className="w-4 h-4 text-primary" />
                                    <span>{tenant.company}</span>
                                </div>
                            </div>

                            <div>
                                <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Admin Email</label>
                                <div className="mt-1 flex items-center gap-2 text-text">
                                    <Mail className="w-4 h-4 text-primary" />
                                    <span className="truncate">{tenant.email}</span>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</label>
                                <div className="mt-1">
                                    {getStatusBadge(tenant.status)}
                                </div>
                            </div>

                            <div>
                                <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Tier</label>
                                <div className="mt-1">
                                    <Badge variant="secondary" className="capitalize">{tenant.tier}</Badge>
                                </div>
                            </div>

                            <div>
                                <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Member Since</label>
                                <div className="mt-1 flex items-center gap-2 text-text">
                                    <Calendar className="w-4 h-4 text-primary" />
                                    <span>{new Date(tenant.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Subscription & Tier Management */}
                    <div className="bg-primary/5 rounded-lg p-5 border border-primary/10">
                        <div className="flex items-center gap-2 mb-4">
                            <CreditCard className="w-5 h-5 text-primary" />
                            <h3 className="font-bold text-text">Subscription Plan</h3>
                        </div>

                        <div className="space-y-4">
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                                {['free', 'starter', 'professional', 'enterprise'].map((t) => (
                                    <button
                                        key={t}
                                        onClick={() => setNewTier(t)}
                                        className={`px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all border ${newTier === t
                                                ? 'bg-primary border-primary text-white shadow-lg'
                                                : 'bg-background border-border text-text-secondary hover:border-primary/50'
                                            }`}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>

                            <div className="flex items-center justify-between pt-2">
                                <p className="text-xs text-text-secondary">
                                    Changing the tier will automatically sync resource quotas (Storage, Query limits) to the enforcement system.
                                </p>
                                <Button
                                    size="sm"
                                    onClick={handleTierChange}
                                    disabled={loading || newTier === tenant.tier}
                                    className="bg-primary hover:bg-primary-hover shadow-md"
                                >
                                    {loading ? 'Updating...' : (
                                        <>
                                            <Check className="w-4 h-4 mr-2" />
                                            Update Plans
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    </div>

                    {/* Usage Summary */}
                    <div className="bg-background rounded-lg p-4 border border-border">
                        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider block mb-3">Resource Usage</label>
                        <div className="grid grid-cols-3 gap-4">
                            <div className="text-center border-r border-border">
                                <p className="text-lg font-bold text-text">{tenant.user_count}</p>
                                <p className="text-[10px] text-text-secondary uppercase">Users</p>
                            </div>
                            <div className="text-center border-r border-border">
                                <p className="text-lg font-bold text-text">{tenant.kb_count}</p>
                                <p className="text-[10px] text-text-secondary uppercase">KBs</p>
                            </div>
                            <div className="text-center">
                                <p className="text-lg font-bold text-text">{tenant.storage_gb.toFixed(2)} GB</p>
                                <p className="text-[10px] text-text-secondary uppercase">Storage</p>
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="pt-6 border-t border-border">
                        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider block mb-4 text-error">Danger Zone</label>
                        <div className="flex flex-col gap-3">
                            <div className="flex items-center justify-between p-3 rounded-lg bg-surface-hover/50 border border-border transition-colors hover:bg-surface-hover">
                                <div>
                                    <p className="font-semibold text-text text-sm">
                                        {tenant.status === 'active' ? 'Suspend Account' : 'Reactive Account'}
                                    </p>
                                    <p className="text-xs text-text-secondary">
                                        {tenant.status === 'active'
                                            ? 'Prevent users from logging in and block API calls'
                                            : 'Restore access to the account and all features'}
                                    </p>
                                </div>
                                <Button
                                    variant={tenant.status === 'active' ? 'destructive' : 'outline'}
                                    size="sm"
                                    onClick={handleStatusToggle}
                                    disabled={loading}
                                    className="min-w-[100px]"
                                >
                                    {tenant.status === 'active' ? (
                                        <PauseCircle className="w-4 h-4 mr-2" />
                                    ) : (
                                        <PlayCircle className="w-4 h-4 mr-2" />
                                    )}
                                    {tenant.status === 'active' ? 'Suspend' : 'Activate'}
                                </Button>
                            </div>

                            <div className="flex items-center justify-between p-3 rounded-lg bg-error/5 border border-error/10 transition-colors hover:bg-error/10">
                                <div>
                                    <p className="font-semibold text-error text-sm">Delete Tenant</p>
                                    <p className="text-xs text-text-secondary">Permanently delete all data, users, and configurations</p>
                                </div>
                                <Button
                                    variant="destructive"
                                    size="sm"
                                    onClick={handleDelete}
                                    disabled={loading}
                                    className="min-w-[100px]"
                                >
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete
                                </Button>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col sm:flex-row justify-between items-center pt-6 gap-4 border-t border-border mt-4">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(`/admin/tenants/${tenant.id}`, '_blank')}
                            className="text-primary hover:text-primary-hover p-0 h-auto font-semibold flex items-center gap-1.5 transition-all hover:gap-2"
                        >
                            <ExternalLink className="w-4 h-4" />
                            View Full Detailed Profile
                        </Button>
                        <div className="flex gap-3 w-full sm:w-auto">
                            <Button variant="outline" onClick={onClose} disabled={loading} className="flex-1 sm:flex-none">
                                Close
                            </Button>
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
}
