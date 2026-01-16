import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { gmailAPI } from '../services/api';
import { Card } from '../components/ui/Card';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

export default function GmailCallbackPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
    const [message, setMessage] = useState('Connecting your Gmail account...');

    const hasRun = useRef(false);

    useEffect(() => {
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (hasRun.current) return;
        hasRun.current = true;

        if (error) {
            setStatus('error');
            setMessage(`Google Auth Error: ${error}`);
            return;
        }

        if (!code) {
            setStatus('error');
            setMessage('No authentication code received.');
            return;
        }

        handleCallback(code);
    }, [searchParams]);

    const handleCallback = async (code: string) => {
        try {
            await gmailAPI.auth.handleCallback(code);
            setStatus('success');
            setMessage('Successfully connected! Redirecting...');
            setTimeout(() => {
                navigate('/settings?tab=integrations');
            }, 2000);
        } catch (err: any) {
            setStatus('error');
            setMessage(err.message || 'Failed to complete connection.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-background p-4">
            <Card className="max-w-md w-full p-8 text-center space-y-4">
                {status === 'processing' && (
                    <>
                        <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto" />
                        <h2 className="text-xl font-semibold text-text">Processing...</h2>
                        <p className="text-text-secondary">{message}</p>
                    </>
                )}
                {status === 'success' && (
                    <>
                        <CheckCircle className="w-12 h-12 text-success mx-auto" />
                        <h2 className="text-xl font-semibold text-text">Connected!</h2>
                        <p className="text-text-secondary">{message}</p>
                    </>
                )}
                {status === 'error' && (
                    <>
                        <XCircle className="w-12 h-12 text-error mx-auto" />
                        <h2 className="text-xl font-semibold text-text">Connection Failed</h2>
                        <p className="text-text-secondary">{message}</p>
                        <button
                            onClick={() => navigate('/settings')}
                            className="mt-4 px-4 py-2 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80"
                        >
                            Return to Settings
                        </button>
                    </>
                )}
            </Card>
        </div>
    );
}
