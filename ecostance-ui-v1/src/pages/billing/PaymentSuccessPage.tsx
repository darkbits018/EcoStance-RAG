import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Icons } from '../../components/icons';

const PaymentSuccessPage: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const gateway = searchParams.get('gateway') || 'stripe';
    const sessionId = searchParams.get('session_id');

    useEffect(() => {
        // We could verify the payment here if needed
        console.log(`Payment successful via ${gateway}${sessionId ? ` (Session: ${sessionId})` : ''}`);
    }, [gateway, sessionId]);

    return (
        <div className="min-h-[80vh] flex items-center justify-center p-6 bg-background/50">
            <Card className="max-w-md w-full p-10 text-center border-none shadow-premium relative overflow-hidden group">
                {/* Animated Background Element */}
                <div className="absolute -top-24 -right-24 w-48 h-48 bg-primary/10 rounded-full blur-3xl group-hover:bg-primary/20 transition-colors duration-700" />

                <div className="relative z-10">
                    <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-8 shadow-inner border border-green-500/20">
                        <Icons.Check className="w-10 h-10 text-green-500" strokeWidth={3} />
                    </div>

                    <h1 className="text-3xl font-black text-text mb-4 tracking-tight">Payment Successful!</h1>
                    <p className="text-text-secondary mb-10 leading-relaxed font-medium">
                        Your subscription has been updated. You now have full access to all the features included in your new plan.
                    </p>

                    <div className="bg-surface p-6 rounded-2xl border border-border/50 mb-10 text-left">
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-[10px] font-black uppercase tracking-widest opacity-40">Status</span>
                            <span className="text-[10px] font-black uppercase tracking-widest text-green-500 bg-green-500/10 px-2 py-1 rounded">Confirmed</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-[10px] font-black uppercase tracking-widest opacity-40">Gateway</span>
                            <span className="text-[10px] font-black uppercase tracking-widest text-text opacity-70">{gateway.toUpperCase()}</span>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <Button
                            onClick={() => navigate('/')}
                            className="w-full h-14 font-black uppercase tracking-[0.2em] text-[10px] rounded-xl shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all"
                        >
                            Go to Dashboard
                        </Button>
                        <Button
                            variant="outline"
                            onClick={() => navigate('/settings')}
                            className="w-full h-14 font-black uppercase tracking-[0.2em] text-[10px] rounded-xl hover:bg-surface-hover transition-all"
                        >
                            View Billing Settings
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
};

export default PaymentSuccessPage;
