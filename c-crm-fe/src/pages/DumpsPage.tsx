import React, { useEffect, useState } from 'react';
import { dumpService, type EmailDumpTask } from '../services/dumpService';
import { authService, type GmailConnection } from '../services/authService';
import { Plus, Play, RefreshCw, AlertCircle, CheckCircle2, Clock, Trash2 } from 'lucide-react';

export const DumpsPage: React.FC = () => {
    const [dumps, setDumps] = useState<EmailDumpTask[]>([]);
    const [connections, setConnections] = useState<GmailConnection[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);

    // Form State
    const [selectedConnection, setSelectedConnection] = useState('');
    const [criteriaType, setCriteriaType] = useState<'RECIPIENT' | 'LABEL'>('RECIPIENT');
    const [criteriaValue, setCriteriaValue] = useState('');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            // Fetch both dumps and connections (needed for creating new dump)
            const [dumpsData, cxData] = await Promise.all([
                dumpService.getAllDumps(),
                authService.listConnections()
            ]);
            setDumps(dumpsData.sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime()));
            setConnections(cxData);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedConnection || !criteriaValue) return;

        setSubmitting(true);
        try {
            await dumpService.createDump({
                connection_id: selectedConnection,
                criteria_type: criteriaType,
                criteria_value: criteriaValue
            });
            setShowCreateForm(false);
            setCriteriaValue('');
            loadData(); // Refresh list immediately
        } catch (err) {
            console.error(err);
            alert('Failed to start dump');
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this task?')) return;
        try {
            await dumpService.deleteDump(id);
            setDumps(prev => prev.filter(d => d.id !== id));
        } catch (err) {
            console.error(err);
            alert('Failed to delete task');
        }
    };

    const handleRerun = async (id: string) => {
        try {
            await dumpService.rerunDump(id);
            loadData(); // Will show the new pending task at top
        } catch (err) {
            console.error(err);
            alert('Failed to rerun update');
        }
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'COMPLETED': return <CheckCircle2 size={18} color="#4ade80" />;
            case 'FAILED': return <AlertCircle size={18} color="#ef4444" />;
            case 'PROCESSING': return <RefreshCw size={18} className="animate-spin text-blue-400" />;
            default: return <Clock size={18} color="#94a3b8" />;
        }
    };

    return (
        <div style={{ padding: '2rem' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Data Dumps</h1>
                    <p style={{ color: 'var(--color-text-muted)' }}>Schedule and monitor email fetches.</p>
                </div>
                <button
                    onClick={() => setShowCreateForm(true)}
                    className="glass-button primary"
                >
                    <Plus size={18} style={{ marginRight: '0.5rem' }} /> New Dump Task
                </button>
            </div>

            {/* Create Form Modal */}
            {showCreateForm && (
                <div style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <div onClick={() => setShowCreateForm(false)} style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.7)' }} />
                    <div className="glass-panel" style={{ width: '100%', maxWidth: '500px', position: 'relative', padding: '2rem' }}>
                        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>New Dump Task</h2>

                        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div style={{ flex: 1, minWidth: '200px' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Connection</label>
                                <select
                                    className="glass-input"
                                    value={selectedConnection}
                                    onChange={e => setSelectedConnection(e.target.value)}
                                    required
                                >
                                    <option value="">Select Account...</option>
                                    {connections.map(c => (
                                        <option key={c.id} value={c.id}>{c.email_address}</option>
                                    ))}
                                </select>
                            </div>

                            <div style={{ width: '150px' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Type</label>
                                <select
                                    className="glass-input"
                                    value={criteriaType}
                                    onChange={e => setCriteriaType(e.target.value as any)}
                                >
                                    <option value="RECIPIENT">Recipient</option>
                                    <option value="LABEL">Label</option>
                                </select>
                            </div>

                            <div style={{ flex: 2, minWidth: '200px' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Value</label>
                                <input
                                    type="text"
                                    className="glass-input"
                                    placeholder={criteriaType === 'RECIPIENT' ? 'e.g. client@example.com' : 'e.g. INBOX'}
                                    value={criteriaValue}
                                    onChange={e => setCriteriaValue(e.target.value)}
                                    required
                                />
                            </div>

                            <button type="submit" className="glass-button" disabled={submitting}>
                                {submitting ? 'Starting...' : <div className="flex-center" style={{ gap: '0.5rem' }}><Play size={16} /> Start</div>}
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Dumps List */}
            <div className="glass-panel" style={{ overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead>
                        <tr style={{ borderBottom: 'var(--border-glass)', background: 'rgba(0,0,0,0.2)' }}>
                            <th style={{ padding: '1rem', fontWeight: '600' }}>Status</th>
                            <th style={{ padding: '1rem', fontWeight: '600' }}>Criteria</th>
                            <th style={{ padding: '1rem', fontWeight: '600' }}>Value</th>
                            <th style={{ padding: '1rem', fontWeight: '600' }}>Started At</th>
                            <th style={{ padding: '1rem', fontWeight: '600', textAlign: 'right' }}>Emails</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && dumps.length === 0 ? (
                            <tr><td colSpan={5} style={{ padding: '2rem', textAlign: 'center' }}>Loading...</td></tr>
                        ) : dumps.length === 0 ? (
                            <tr><td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>No dumps found.</td></tr>
                        ) : (
                            dumps.map(dump => (
                                <tr key={dump.id} style={{ borderBottom: 'var(--border-glass)' }}>
                                    <td style={{ padding: '1rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            {getStatusIcon(dump.status)}
                                            <span style={{ fontSize: '0.9rem' }}>{dump.status}</span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '1rem', fontSize: '0.9rem' }}>{dump.criteria_type}</td>
                                    <td style={{ padding: '1rem', fontFamily: 'monospace', color: 'var(--color-accent)' }}>{dump.criteria_value}</td>
                                    <td style={{ padding: '1rem', fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
                                        {new Date(dump.started_at).toLocaleString()}
                                    </td>
                                    <td style={{ padding: '1rem', textAlign: 'right' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '1rem' }}>
                                            <span style={{ fontWeight: 'bold' }}>{dump.total_emails}</span>

                                            <button
                                                onClick={() => handleRerun(dump.id)}
                                                style={{
                                                    background: 'none', border: 'none', color: '#60a5fa',
                                                    cursor: 'pointer', padding: '0.4rem', borderRadius: '0.4rem',
                                                    display: 'flex', alignItems: 'center'
                                                }}
                                                className="hover:bg-white/10"
                                                title="Run Again"
                                            >
                                                <RefreshCw size={16} />
                                            </button>

                                            <button
                                                onClick={() => handleDelete(dump.id)}
                                                style={{
                                                    background: 'none', border: 'none', color: '#ef4444',
                                                    cursor: 'pointer', padding: '0.4rem', borderRadius: '0.4rem',
                                                    display: 'flex', alignItems: 'center'
                                                }}
                                                className="hover:bg-white/10"
                                                title="Delete Task"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
