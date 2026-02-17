import React from 'react';
import { Card } from '../../ui/Card';
import { Icons } from '../../icons';

interface ImpactStatsProps {
    contribution: string | number;
    trees_equivalent: number;
    rank: string;
}

export const ImpactStats: React.FC<ImpactStatsProps> = ({
    contribution,
    trees_equivalent,
    rank,
}) => {
    return (
        <Card className="p-4 bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
            <div className="flex items-center gap-2 mb-4">
                <Icons.Activity className="w-5 h-5 text-primary" />
                <h4 className="font-bold text-text">Your Environmental Impact</h4>
            </div>

            <div className="grid grid-cols-1 gap-4">
                <div className="flex items-center gap-4 bg-surface/50 p-3 rounded-lg border border-border">
                    <div className="p-3 bg-secondary/10 rounded-full">
                        <Icons.TrendingUp className="w-6 h-6 text-secondary" />
                    </div>
                    <div>
                        <p className="text-xs text-text-secondary uppercase font-medium">CO2 Offset</p>
                        <p className="text-xl font-bold text-text">{contribution} kg</p>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div className="bg-surface/50 p-3 rounded-lg border border-border flex flex-col items-center text-center">
                        <div className="p-2 mb-2 bg-green-500/10 rounded-lg">
                            <span className="text-xl">🌳</span>
                        </div>
                        <p className="text-[10px] text-text-secondary uppercase font-medium">Trees Equivalent</p>
                        <p className="text-lg font-bold text-green-500">{trees_equivalent}</p>
                    </div>

                    <div className="bg-surface/50 p-3 rounded-lg border border-border flex flex-col items-center text-center">
                        <div className="p-2 mb-2 bg-yellow-500/10 rounded-lg">
                            <Icons.Sparkles className="w-5 h-5 text-yellow-500" />
                        </div>
                        <p className="text-[10px] text-text-secondary uppercase font-medium">Impact Rank</p>
                        <p className="text-lg font-bold text-text">{rank}</p>
                    </div>
                </div>
            </div>

            <p className="mt-4 text-[11px] text-text-secondary italic text-center">
                "Every ton counts. You're doing great for the planet!"
            </p>
        </Card>
    );
};
