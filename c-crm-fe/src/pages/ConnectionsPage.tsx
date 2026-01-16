import React, { useEffect, useState } from 'react';
import { authService, type GmailConnection } from '../services/authService';
import { LogIn, CheckCircle, XCircle, Loader2 } from 'lucide-react';

export const ConnectionsPage: React.FC = () => {
    const [connections, setConnections] = useState<GmailConnection[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchConnections();
    }, []);

    const fetchConnections = async () => {
        try {
            setLoading(true);
            const data = await authService.listConnections();
            setConnections(data);
        } catch (err) {
            console.error(err);
            // Mocking data for now if API fails (since backend might not be fully ready)
            // Remove this mock in production
            setConnections([
                // { id: '1', email_address: 'mock_user@example.com', is_active: true, token_expiry: '2025-01-01' }
            ]);
            setError('Failed to load connections. Ensure backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const handleConnect = async () => {
        try {
            const response = await authService.getLoginUrl();
            const data: any = response; // Handle generic object

            if (data.error) {
                setError(data.error);
                return;
            }
            if (data.url) {
                window.location.href = data.url;
            } else {
                // Fallback if just string
                const urlStr = typeof response === 'string' ? response : (response as any).url;
                if (urlStr) window.location.href = urlStr;
            }
        } catch (err) {
            console.error('Failed to initiate login', err);
            setError('Could not initiate Google Login.');
        }
    };

    return (
        <div className="container-main">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 className="page-title">Connections</h1>
                    <p className="page-subtitle">Manage your Gmail integrations</p>
                </div>
                <button className="glass-button" onClick={handleConnect}>
                    <div className="flex-center" style={{ gap: '0.5rem' }}>
                        <LogIn size={18} />
                        <span>Connect New Account</span>
                    </div>
                </button>
            </div>

            {error && (
                <div className="glass-panel" style={{ padding: '1rem', marginBottom: '1rem', borderColor: 'rgba(255, 100, 100, 0.3)', color: '#ffaaaa' }}>
                    {error}
                </div>
            )}

            {loading ? (
                <div className="flex-center" style={{ height: '200px' }}>
                    <Loader2 className="animate-spin" size={32} />
                </div>
            ) : (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {connections.length === 0 && !error && (
                        <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                            No active connections found. Click "Connect New Account" to get started.
                        </div>
                    )}

                    {connections.map(conn => (
                        <div key={conn.id} className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <div style={{
                                    width: '48px', height: '48px', borderRadius: '50%',
                                    background: 'var(--color-primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center'
                                }}>
                                    <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{conn.email_address[0].toUpperCase()}</span>
                                </div>
                                <div>
                                    <h3 style={{ fontSize: '1.1rem', fontWeight: '600' }}>{conn.email_address}</h3>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: conn.is_active ? '#4ade80' : '#f87171' }}>
                                        {conn.is_active ? <CheckCircle size={14} /> : <XCircle size={14} />}
                                        <span>{conn.is_active ? 'Active' : 'Expired'}</span>
                                    </div>
                                </div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
                                    Expires: {new Date(conn.token_expiry).toLocaleDateString()}
                                </p>
                                {/* Maybe a reconnect button if expired */}
                                {!conn.is_active && <button className="glass-button secondary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}>Reconnect</button>}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
