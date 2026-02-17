import React from 'react';
import { Card } from '../../ui/Card';
import { Icons } from '../../icons';
import { Badge } from '../../ui/Badge';

interface CertificateCardProps {
    project: string;
    status: string;
    date: string;
    tonnage: string | number;
}

export const CertificateCard: React.FC<CertificateCardProps> = ({
    project,
    status,
    date,
    tonnage,
}) => {
    return (
        <Card className="p-4 bg-surface border-border overflow-hidden relative">
            <div className="absolute top-0 right-0 p-2 opacity-10">
                <Icons.Shield className="w-16 h-16" />
            </div>

            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                    <div className="p-2 bg-primary/10 rounded-lg">
                        <Icons.CheckCircle className="w-5 h-5 text-primary" />
                    </div>
                    <h4 className="font-semibold text-text">Carbon Offset Certificate</h4>
                </div>
                <Badge variant={status.toLowerCase() === 'verified' ? 'outline' : 'secondary'}>
                    {status}
                </Badge>
            </div>

            <div className="space-y-3">
                <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider font-medium">Project Name</p>
                    <p className="text-sm text-text font-medium">{project}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <p className="text-xs text-text-secondary uppercase tracking-wider font-medium">Issue Date</p>
                        <p className="text-sm text-text font-medium">{date}</p>
                    </div>
                    <div>
                        <p className="text-xs text-text-secondary uppercase tracking-wider font-medium">Total Tonnage</p>
                        <p className="text-sm text-primary font-bold">{tonnage} tCO2e</p>
                    </div>
                </div>
            </div>

            <div className="mt-4 pt-3 border-t border-border flex justify-between items-center text-[10px] text-text-secondary">
                <span>Verified by EcoStance Orchestrator</span>
                <span className="flex items-center gap-1">
                    <Icons.ExternalLink className="w-3 h-3" />
                    View Blockchain Receipt
                </span>
            </div>
        </Card>
    );
};
