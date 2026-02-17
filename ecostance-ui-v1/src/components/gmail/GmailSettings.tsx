import { useState, useEffect } from 'react';
import { gmailAPI } from '../../services/api';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Mail, CheckCircle, AlertTriangle } from 'lucide-react';
import GmailRecipientTable from './GmailRecipientTable';
import GmailScheduleConfig from './GmailScheduleConfig';
import GmailHistoryTable from './GmailHistoryTable';

import { RefreshCw } from 'lucide-react';

interface GmailSettingsProps {
    tenant: any;
}

export default function GmailSettings({ tenant }: GmailSettingsProps) {
    const [status, setStatus] = useState<{ connected: boolean; email: string | null }>({
        connected: false,
        email: null
    });
    const [isLoadingStatus, setIsLoadingStatus] = useState(true);
    const [isVerifying, setIsVerifying] = useState(false);

    useEffect(() => {
        // Explicitly clear status when switching tenants to avoid "trailing" stale state
        setStatus({ connected: false, email: null });
        fetchStatus();
    }, [tenant?.id]); // Re-fetch when tenant switches

    const fetchStatus = async () => {
        setIsLoadingStatus(true);
        try {
            const data = await gmailAPI.auth.getStatus();
            console.log('[GmailSettings] Connection status:', data);
            setStatus(data);
        } catch (err) {
            console.error('[GmailSettings] Failed to fetch status:', err);
            setStatus({ connected: false, email: null });
        } finally {
            setIsLoadingStatus(false);
            setIsVerifying(false);
        }
    };

    const verifyConnection = async () => {
        setIsVerifying(true);
        await fetchStatus();
    };

    const handleConnect = async () => {
        try {
            const { auth_url } = await gmailAPI.auth.getAuthUrl();
            window.location.href = auth_url;
        } catch (err) {
            console.error('Failed to get auth url', err);
            alert('Failed to initiate connection. Please ensure you have GMAIL_CONFIGURE permissions.');
        }
    };

    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleSyncComplete = () => {
        setRefreshTrigger(prev => prev + 1);
    };

    return (
        <div className="space-y-6">
            <Card className="p-6 bg-surface border-border">
                <div className="flex items-start justify-between">
                    <div className="flex gap-4">
                        <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
                            <Mail className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-text">Gmail Integration</h2>
                            <p className="text-sm text-text-secondary mt-1">Connect your Gmail account to automatically ingest emails into your Knowledge Base.</p>

                            <div className="mt-4 flex items-center gap-2">
                                {isLoadingStatus ? (
                                    <div className="flex items-center gap-2 text-text-secondary px-3 py-1 rounded-full text-sm">
                                        <RefreshCw className="w-4 h-4 animate-spin" />
                                        Checking status...
                                    </div>
                                ) : status.connected ? (
                                    <div className="flex items-center gap-2 text-success font-medium bg-success/10 px-3 py-1 rounded-full text-sm">
                                        <CheckCircle className="w-4 h-4" />
                                        Connected {status.email && `as ${status.email}`}
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-2 text-warning font-medium bg-warning/10 px-3 py-1 rounded-full text-sm">
                                        <AlertTriangle className="w-4 h-4" />
                                        {isVerifying ? 'Verifying status...' : 'Not Connected'}
                                    </div>
                                )}
                                <Button variant="ghost" size="sm" onClick={verifyConnection} title="Refresh Status" disabled={isLoadingStatus || isVerifying}>
                                    <RefreshCw className={`w-4 h-4 text-text-secondary ${(isLoadingStatus || isVerifying) ? 'animate-spin' : ''}`} />
                                </Button>
                            </div>
                        </div>
                    </div>

                    {!isLoadingStatus && !status.connected && (
                        <Button onClick={handleConnect}>
                            Connect Gmail Account
                        </Button>
                    )}
                </div>
            </Card>

            {status.connected && (
                <div className="space-y-8">
                    <GmailRecipientTable />
                    <div className="border-t border-border pt-8">
                        <GmailScheduleConfig onSyncComplete={handleSyncComplete} />
                    </div>
                    <div className="border-t border-border pt-8">
                        <GmailHistoryTable refreshTrigger={refreshTrigger} />
                    </div>
                </div>
            )}
        </div>
    );
}
