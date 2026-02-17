import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Icons } from '../../components/icons';

const PaymentCancelPage: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-[80vh] flex items-center justify-center p-6 bg-background/50">
            <Card className="max-w-md w-full p-10 text-center border-none shadow-premium relative overflow-hidden group">
                {/* Animated Background Element */}
                <div className="absolute -top-24 -right-24 w-48 h-48 bg-error/10 rounded-full blur-3xl group-hover:bg-error/20 transition-colors duration-700" />

                <div className="relative z-10">
                    <div className="w-20 h-20 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-8 shadow-inner border border-error/20">
                        <Icons.X className="w-10 h-10 text-error" strokeWidth={3} />
                    </div>

                    <h1 className="text-3xl font-black text-text mb-4 tracking-tight">Checkout Cancelled</h1>
                    <p className="text-text-secondary mb-10 leading-relaxed font-medium">
                        The payment process was not completed. No charges were made to your account.
                    </p>

                    <p className="text-xs text-text-secondary/60 mb-10 font-bold opacity-80 uppercase tracking-widest leading-relaxed px-8">
                        Changed your mind? You can always upgrade later from your settings.
                    </p>

                    <div className="space-y-4">
                        <Button
                            onClick={() => navigate('/settings')}
                            className="w-full h-14 font-black uppercase tracking-[0.2em] text-[10px] rounded-xl shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all"
                        >
                            Back to Pricing
                        </Button>
                        <Button
                            variant="outline"
                            onClick={() => navigate('/')}
                            className="w-full h-14 font-black uppercase tracking-[0.2em] text-[10px] rounded-xl hover:bg-surface-hover transition-all"
                        >
                            Cancel and Exit
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
};

export default PaymentCancelPage;
