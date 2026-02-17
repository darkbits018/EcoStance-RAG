import React from 'react';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { Icons } from './icons';
import { cn } from '../lib/utils';
import { billingAPI } from '../services/api';
import { useAuth } from '../context/AuthContext.v2';

interface PlanFeature {
    text: string;
    included: boolean;
}

interface Plan {
    id: 'free_trial' | 'business' | 'enterprise';
    name: string;
    price: string;
    description: string;
    features: PlanFeature[];
    isPopular?: boolean;
    buttonText: string;
    gradient?: string;
    prices: {
        USD: string;
        INR: string;
    };
}

const PLANS: Plan[] = [
    {
        id: 'free_trial',
        name: 'Free Trial',
        price: '0',
        prices: { USD: '0', INR: '0' },
        description: 'Experience the power of EcoStance AI',
        buttonText: 'Current Plan',
        features: [
            { text: '5,000 Documents', included: true },
            { text: '500 Queries / day', included: true },
            { text: '5GB Storage', included: true },
            { text: 'Neutral Assistant Persona', included: true },
            { text: 'KB & DB Tools', included: true },
            { text: 'Custom Tools', included: false },
        ]
    },
    {
        id: 'business',
        name: 'Business',
        price: '29',
        prices: { USD: '29', INR: '2499' },
        description: 'For growing teams and businesses',
        isPopular: true,
        buttonText: 'Upgrade to Business',
        gradient: 'from-primary to-accent',
        features: [
            { text: '50,000 Documents', included: true },
            { text: '5,000 Queries / day', included: true },
            { text: '50GB Storage', included: true },
            { text: 'Fixed Professional Persona', included: true },
            { text: 'Full KB & DB Access', included: true },
            { text: 'Priority Email Support', included: true },
        ]
    },
    {
        id: 'enterprise',
        name: 'Enterprise',
        price: 'Custom',
        prices: { USD: 'Custom', INR: 'Custom' },
        description: 'Scale your AI operations with confidence',
        buttonText: 'Contact Sales',
        features: [
            { text: 'Unlimited Documents', included: true },
            { text: 'Unlimited Queries', included: true },
            { text: 'Unlimited Storage', included: true },
            { text: 'Custom Persona Branding', included: true },
            { text: 'Custom Tools (Dev-Assisted)', included: true },
            { text: 'Managed Onboarding', included: true },
        ]
    }
];

interface PricingGridProps {
    currentTier: string;
}

export const PricingGrid: React.FC<PricingGridProps> = ({ currentTier }) => {
    const [currency, setCurrency] = React.useState<'USD' | 'INR'>('USD');
    const [loadingPlan, setLoadingPlan] = React.useState<string | null>(null);
    const { user } = useAuth();

    // Standardize current tier for comparison
    const normalizedCurrentTier = (currentTier === 'free' ? 'free_trial' : currentTier).toLowerCase();

    const loadRazorpay = () => {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://checkout.razorpay.com/v1/checkout.js';
            script.onload = () => resolve(true);
            script.onerror = () => resolve(false);
            document.body.appendChild(script);
        });
    };

    const handleUpgrade = async (planId: 'business' | 'enterprise') => {
        if (planId === 'enterprise') {
            window.location.href = 'mailto:sales@ecostance.ai';
            return;
        }

        setLoadingPlan(planId);
        try {
            const res = await billingAPI.createCheckout(planId, currency) as any;

            if (res.provider === 'stripe') {
                window.location.href = res.checkout_url;
            } else if (res.provider === 'razorpay') {
                const isLoaded = await loadRazorpay();
                if (!isLoaded) {
                    alert('Failed to load Razorpay SDK. Please check your connection.');
                    return;
                }

                const options = {
                    key: res.key_id,
                    amount: res.amount,
                    currency: res.currency,
                    name: "EcoStance AI",
                    description: `${planId.toUpperCase()} Plan Subscription`,
                    order_id: res.order_id,
                    handler: function () {
                        window.location.href = "/billing/success?gateway=razorpay";
                    },
                    prefill: {
                        email: user?.email || "",
                    },
                    theme: { color: "#0066CC" }
                };
                const rzp = new (window as any).Razorpay(options);
                rzp.open();
            }
        } catch (err: any) {
            console.error('Checkout error:', err);
            alert(err.message || 'Failed to initiate checkout');
        } finally {
            setLoadingPlan(null);
        }
    };

    return (
        <section className="py-8">
            <div className="text-center mb-10">
                <h2 className="text-3xl font-extrabold text-text mb-4 tracking-tight">EcoStance Plans & Pricing</h2>
                <p className="text-text-secondary max-w-2xl mx-auto text-lg mb-8">
                    Simple, transparent pricing to power your AI-driven organization.
                </p>

                {/* Currency Switcher */}
                <div className="flex items-center justify-center gap-4 mb-4">
                    <span className={cn("text-sm font-bold transition-colors", currency === 'USD' ? "text-text" : "text-text-secondary opacity-50")}>USD</span>
                    <button
                        onClick={() => setCurrency(prev => prev === 'USD' ? 'INR' : 'USD')}
                        className="w-14 h-7 bg-surface-hover rounded-full p-1 relative transition-all duration-300 border border-border"
                    >
                        <div className={cn(
                            "w-5 h-5 bg-primary rounded-full transition-all duration-300 shadow-lg",
                            currency === 'INR' ? "translate-x-7" : "translate-x-0"
                        )} />
                    </button>
                    <span className={cn("text-sm font-bold transition-colors", currency === 'INR' ? "text-text" : "text-text-secondary opacity-50")}>INR (India)</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto px-4">
                {PLANS.map((plan) => {
                    const isCurrent = normalizedCurrentTier === plan.id;
                    const price = plan.prices[currency];

                    return (
                        <Card
                            key={plan.id}
                            className={cn(
                                "relative flex flex-col p-8 transition-all duration-500 hover:shadow-2xl border-2",
                                plan.isPopular ? "border-primary shadow-xl scale-105 z-10 bg-surface" : "border-border bg-surface/50",
                                isCurrent && "border-primary/50 shadow-glow-primary/10"
                            )}
                        >
                            {plan.isPopular && (
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
                                    <span className="bg-primary text-white text-[10px] font-black uppercase tracking-[0.2em] px-4 py-1.5 rounded-full shadow-lg">
                                        Best Value
                                    </span>
                                </div>
                            )}

                            {isCurrent && (
                                <div className="absolute top-4 right-4">
                                    <div className="flex items-center gap-1.5 px-3 py-1 bg-primary/10 text-primary rounded-full text-[10px] font-black uppercase tracking-wider border border-primary/20">
                                        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                                        Current Plan
                                    </div>
                                </div>
                            )}

                            <div className="mb-8">
                                <h3 className="text-2xl font-black text-text mb-2 tracking-tight">{plan.name}</h3>
                                <p className="text-sm text-text-secondary leading-relaxed font-medium">{plan.description}</p>
                            </div>

                            <div className="mb-10 flex items-baseline gap-1">
                                <span className="text-5xl font-black text-text tracking-tighter">
                                    {price === 'Custom' ? 'Custom' : (currency === 'USD' ? `$${price}` : `₹${price}`)}
                                </span>
                                {price !== 'Custom' && (
                                    <span className="text-text-secondary font-bold text-lg opacity-60">/mo</span>
                                )}
                            </div>

                            <div className="space-y-4 mb-10 flex-grow">
                                {plan.features.map((feature, idx) => (
                                    <div key={idx} className="flex items-start gap-3">
                                        {feature.included ? (
                                            <div className="mt-0.5 p-1 rounded-full bg-primary/10 text-primary">
                                                <Icons.Check className="w-3 h-3" strokeWidth={3} />
                                            </div>
                                        ) : (
                                            <div className="mt-0.5 p-1 rounded-full bg-text-secondary/10 text-text-secondary">
                                                <Icons.X className="w-3 h-3 opacity-30" strokeWidth={3} />
                                            </div>
                                        )}
                                        <span className={cn(
                                            "text-sm",
                                            feature.included ? "text-text font-medium" : "text-text-secondary opacity-40"
                                        )}>
                                            {feature.text}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            <Button
                                variant={plan.isPopular ? 'primary' : 'outline'}
                                onClick={() => handleUpgrade(plan.id as any)}
                                className={cn(
                                    "w-full font-black uppercase tracking-[0.2em] text-[10px] h-12 rounded-xl transition-all duration-300",
                                    isCurrent ? "bg-transparent border-primary text-primary cursor-default pointer-events-none" : "hover:scale-105 active:scale-95"
                                )}
                                disabled={isCurrent || loadingPlan === plan.id}
                            >
                                {loadingPlan === plan.id ? (
                                    <Icons.Spinner className="w-4 h-4 animate-spin" />
                                ) : (
                                    isCurrent ? 'Active Plan' : plan.buttonText
                                )}
                            </Button>

                            {plan.id === 'enterprise' && !isCurrent && (
                                <Button
                                    variant="outline"
                                    onClick={() => window.location.href = 'mailto:sales@ecostance.ai'}
                                    className="w-full font-black uppercase tracking-[0.2em] text-[10px] h-12 rounded-xl mt-3 hover:bg-surface-hover"
                                >
                                    Speak to Sales
                                </Button>
                            )}
                        </Card>
                    );
                })}
            </div>

            <div className="mt-16 max-w-6xl mx-auto px-4">
                <div className="p-10 bg-gradient-to-br from-surface to-surface-hover rounded-3xl border border-border flex flex-col md:flex-row items-center justify-between gap-10">
                    <div className="flex items-center gap-6">
                        <div className="p-4 bg-primary/10 rounded-2xl shadow-inner">
                            <Icons.Shield className="w-8 h-8 text-primary" />
                        </div>
                        <div>
                            <h4 className="text-xl font-bold text-text mb-1 tracking-tight">Enterprise Infrastructure</h4>
                            <p className="text-sm text-text-secondary font-medium">All plans feature SOC-2 compliant security and high-availability clusters.</p>
                        </div>
                    </div>
                    <div className="flex flex-col items-center md:items-end gap-3">
                        <p className="text-xs font-bold text-text-secondary uppercase tracking-widest opacity-60">Need a dedicated instance?</p>
                        <button className="px-8 py-3 bg-text text-background rounded-full font-black uppercase tracking-widest text-[10px] hover:scale-105 transition-transform active:scale-95 shadow-xl">
                            Talk to Success Agent
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
};
