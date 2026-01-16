import React, { useEffect, useState } from 'react';
import { authService } from '../services/authService';
import { dumpService } from '../services/dumpService';
import { Link } from 'react-router-dom';
import { Database, Link2, ArrowRight } from 'lucide-react';

export const DashboardPage: React.FC = () => {
    const [stats, setStats] = useState({ connections: 0, dumps: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchStats() {
            try {
                const [conn, dumps] = await Promise.all([
                    authService.listConnections(),
                    dumpService.getAllDumps()
                ]);
                setStats({ connections: conn.length, dumps: dumps.length });
            } catch (e) {
                console.error("Failed to load dashboard stats", e);
            } finally {
                setLoading(false);
            }
        }
        fetchStats();
    }, []);

    return (
        <div className="container-main">
            <h1 className="page-title">Dashboard</h1>
            <p className="page-subtitle">Welcome to your Custom CRM.</p>

            {loading ? (
                <div style={{ color: 'var(--color-text-muted)' }}>Loading overview...</div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginTop: '2rem' }}>
                    {/* Connection Card */}
                    <div className="glass-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div>
                                <h3 style={{ fontSize: '1.2rem', color: 'var(--color-text-muted)' }}>Active Connection</h3>
                                <div style={{ fontSize: '3rem', fontWeight: '700', lineHeight: 1.2 }}>{stats.connections}</div>
                            </div>
                            <div style={{ padding: '0.8rem', background: 'hsla(var(--hue-primary), 50%, 50%, 0.2)', borderRadius: '12px' }}>
                                <Link2 size={24} color="var(--color-primary)" />
                            </div>
                        </div>
                        <div style={{ marginTop: 'auto' }}>
                            <Link to="/connections" style={{ color: 'var(--color-primary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: '500' }}>
                                Manage Accounts <ArrowRight size={16} />
                            </Link>
                        </div>
                    </div>

                    {/* Dumps Card */}
                    <div className="glass-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div>
                                <h3 style={{ fontSize: '1.2rem', color: 'var(--color-text-muted)' }}>Data Dumps</h3>
                                <div style={{ fontSize: '3rem', fontWeight: '700', lineHeight: 1.2 }}>{stats.dumps}</div>
                            </div>
                            <div style={{ padding: '0.8rem', background: 'hsla(var(--hue-accent), 50%, 50%, 0.2)', borderRadius: '12px' }}>
                                <Database size={24} color="var(--color-accent)" />
                            </div>
                        </div>
                        <div style={{ marginTop: 'auto' }}>
                            <Link to="/dumps" style={{ color: 'var(--color-accent)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: '500' }}>
                                View Task History <ArrowRight size={16} />
                            </Link>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
