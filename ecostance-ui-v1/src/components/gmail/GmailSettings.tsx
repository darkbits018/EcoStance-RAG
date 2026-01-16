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
    onRefresh: () => Promise<void>;
}

export default function GmailSettings({ tenant, onRefresh }: GmailSettingsProps) {
    // access gmail_config safely
    const gmailConfig = tenant?.gmail_config || {};

    // Debug logging
    console.log('[GmailSettings] Tenant Gmail Config:', gmailConfig);

    // Check truthy value (handles true, 1, "true")
    // We also use local state to override if we verify connection via API successfully
    const propsConnected = !!gmailConfig.is_connected;

    const [isVerifiedConnected, setIsVerifiedConnected] = useState(false);
    const [isVerifying, setIsVerifying] = useState(false);

    // Determine effective connection status
    const connected = propsConnected || isVerifiedConnected;
    const connectedEmail = gmailConfig.connected_email || (isVerifiedConnected ? 'Gmail Account' : null);

    useEffect(() => {
        // If props say not connected, let's verify manually by trying to fetch data
        if (!propsConnected) {
            verifyConnection();
        }
    }, [propsConnected]);

    const verifyConnection = async () => {
        setIsVerifying(true);
        try {
            // Try to fetch recipients as a way to check if we have a valid token
            await gmailAPI.recipients.list();
            console.log('[GmailSettings] Verification successful - We are connected!');
            setIsVerifiedConnected(true);
        } catch (err) {
            console.log('[GmailSettings] Verification failed - Not connected', err);
            setIsVerifiedConnected(false);
            if (isVerifiedConnected) setIsVerifiedConnected(false); // Reset if it was true
        } finally {
            setIsVerifying(false);
        }
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
                {/* ... existing header code ... */}
                <div className="flex items-start justify-between">
                    <div className="flex gap-4">
                        <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
                            <Mail className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-text">Gmail Integration</h2>
                            <p className="text-sm text-text-secondary mt-1">Connect your Gmail account to automatically ingest emails into your Knowledge Base.</p>

                            <div className="mt-4 flex items-center gap-2">
                                {connected ? (
                                    <div className="flex items-center gap-2 text-success font-medium bg-success/10 px-3 py-1 rounded-full text-sm">
                                        <CheckCircle className="w-4 h-4" />
                                        Connected {connectedEmail && `as ${connectedEmail}`}
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-2 text-warning font-medium bg-warning/10 px-3 py-1 rounded-full text-sm">
                                        <AlertTriangle className="w-4 h-4" />
                                        {isVerifying ? 'Verifying status...' : 'Not Connected'}
                                    </div>
                                )}
                                <Button variant="ghost" size="sm" onClick={() => { verifyConnection(); onRefresh(); }} title="Refresh Status">
                                    <RefreshCw className={`w-4 h-4 text-text-secondary ${isVerifying ? 'animate-spin' : ''}`} />
                                </Button>
                            </div>
                            {/* Debug Info */}
                            <div className="mt-2 text-xs text-text-secondary">
                                <p>Config Status: {connected ? 'Active' : 'Inactive'}</p>
                                <details>
                                    <summary className="cursor-pointer hover:text-text">Raw Config</summary>
                                    <pre className="mt-1 p-2 bg-background rounded border border-border overflow-auto">
                                        {JSON.stringify(gmailConfig, null, 2)}
                                    </pre>
                                </details>
                            </div>
                        </div>
                    </div>

                    {!connected && (
                        <Button onClick={handleConnect}>
                            Connect Gmail Account
                        </Button>
                    )}
                </div>
            </Card>

            {connected && (
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
