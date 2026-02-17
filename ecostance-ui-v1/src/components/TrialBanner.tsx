import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../context/AuthContext.v2';
import { AlertCircle, Clock, Calendar as CalendarIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { cn } from '../lib/utils';

export const TrialBanner: React.FC = () => {
    const { trialEndsAt, billingTier } = useAuth();
    const navigate = useNavigate();
    const [now, setNow] = useState(new Date());

    // Update the "now" time every minute to keep calculation precise
    useEffect(() => {
        const timer = setInterval(() => setNow(new Date()), 60000);
        return () => clearInterval(timer);
    }, []);

    // According to BILLING_SPEC.md, trial key is 'free_trial'
    // Supporting 'free' for backward compatibility as requested in data
    const normalizedTier = billingTier?.toLowerCase();
    const isTrial = normalizedTier === 'free_trial' || normalizedTier === 'free';

    // Calculate time details
    const timeInfo = useMemo(() => {
        if (!trialEndsAt) return null;

        const trialEnd = new Date(trialEndsAt);
        const diffTime = trialEnd.getTime() - now.getTime();
        const isExpired = diffTime <= 0;

        if (isExpired) return { isExpired: true };

        const totalMinutes = Math.floor(diffTime / (1000 * 60));
        const totalHours = Math.floor(totalMinutes / 60);
        const days = Math.floor(totalHours / 24);
        const hours = totalHours % 24;
        const minutes = totalMinutes % 60;

        return {
            isExpired: false,
            days,
            hours,
            minutes,
            diffDays: days,
            formattedEndDate: trialEnd.toLocaleDateString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric'
            })
        };
    }, [trialEndsAt, now]);

    // Only show for free_trial tier
    if (!trialEndsAt || !isTrial || !timeInfo) {
        return null;
    }

    if (timeInfo.isExpired) {
        return (
            <div className="px-6 py-2.5 flex items-center justify-between bg-gradient-to-r from-red-600 to-red-500 text-white shadow-xl relative overflow-hidden ring-1 ring-inset ring-red-400/50">
                <div className="absolute inset-0 bg-white/5 animate-pulse" />
                <div className="flex items-center gap-4 relative z-10">
                    <div className="p-1.5 bg-white/20 rounded-lg shadow-inner">
                        <AlertCircle className="w-4 h-4" />
                    </div>
                    <div>
                        <p className="text-sm font-bold tracking-tight">Free Trial Expired</p>
                        <p className="text-xs opacity-90">Please upgrade to Business or Enterprise to continue using EcoStance AI.</p>
                    </div>
                </div>
                <button
                    onClick={() => navigate('/settings?tab=billing')}
                    className="bg-white text-red-600 text-[10px] font-black uppercase tracking-[0.2em] px-6 py-2 rounded-full hover:bg-gray-100 transition-all shadow-lg active:scale-95 z-10"
                >
                    Upgrade Plan
                </button>
            </div>
        );
    }

    const days = timeInfo.days ?? 0;
    const hours = timeInfo.hours ?? 0;
    const minutes = timeInfo.minutes ?? 0;
    const formattedEndDate = timeInfo.formattedEndDate ?? '';
    const isUrgent = days <= 3;
    const isWarning = days <= 7;

    return (
        <div className={cn(
            "px-6 py-2.5 flex items-center justify-between shadow-2xl transition-all duration-500 relative overflow-hidden ring-1 ring-inset",
            isUrgent
                ? "bg-gradient-to-r from-orange-600 to-error text-white ring-orange-500/50"
                : isWarning
                    ? "bg-gradient-to-r from-amber-500 to-orange-500 text-white ring-amber-400/50"
                    : "bg-gradient-to-r from-primary/20 via-surface to-primary/10 border-b border-primary/40 text-text backdrop-blur-2xl ring-primary/20"
        )}>
            {/* Shimmer effect for ambient animation */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full animate-shimmer pointer-events-none" />

            <div className="flex items-center gap-4 relative z-10">
                <div className={cn(
                    "p-1.5 rounded-lg shadow-inner flex items-center justify-center",
                    (isWarning || isUrgent) ? "bg-white/20" : "bg-primary/20 text-primary border border-primary/30"
                )}>
                    <Clock className="w-4 h-4" />
                </div>

                <div className="flex flex-col lg:flex-row lg:items-center gap-1 lg:gap-4">
                    <div className="flex items-center gap-2">
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-80 decoration-primary/50">
                            Free Trial Active
                        </p>
                        <div className={cn("w-1 h-1 rounded-full", (isWarning || isUrgent) ? "bg-white/40" : "bg-primary/40")} />
                        <p className="text-sm font-bold tracking-tight">
                            {days > 0 ? (
                                <span>{days} {days === 1 ? 'day' : 'days'} remaining</span>
                            ) : (
                                <span className="animate-pulse text-red-400 font-black">
                                    {hours}h {minutes}m left!
                                </span>
                            )}
                        </p>
                    </div>

                    <div className="flex items-center gap-3 font-medium">
                        <div className={cn(
                            "hidden sm:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] uppercase tracking-wider font-black",
                            (isWarning || isUrgent) ? "bg-white/10 text-white" : "bg-primary/10 text-primary border border-primary/10"
                        )}>
                            <CalendarIcon className="w-3 h-3" />
                            <span>Ends {formattedEndDate}</span>
                        </div>
                        {!isWarning && !isUrgent && (
                            <span className="hidden xl:inline text-text-secondary font-medium text-[11px] opacity-70">
                                — Scale to Business or Enterprise for production workloads
                            </span>
                        )}
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-3 relative z-10">
                <button
                    onClick={() => navigate('/settings?tab=billing')}
                    className={cn(
                        "text-[10px] font-black uppercase tracking-[0.22em] px-6 py-2 rounded-full transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg",
                        (isWarning || isUrgent)
                            ? "bg-white text-orange-600 hover:bg-white/90 shadow-black/20"
                            : "bg-primary text-white hover:shadow-[0_0_20px_rgba(var(--primary-rgb),0.3)] shadow-primary/20"
                    )}
                >
                    Choose Plan
                </button>
            </div>
        </div>
    );
};
