import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../ui/Button';
import { Icons } from '../../icons';

interface UrlActionProps {
    label: string;
    url: string;
    type?: 'primary' | 'secondary' | 'outline';
}

export const UrlAction: React.FC<UrlActionProps> = ({ label, url, type = 'primary' }) => {
    const navigate = useNavigate();

    const handleClick = () => {
        if (url.startsWith('/') || !url.startsWith('http')) {
            navigate(url);
        } else {
            window.open(url, '_blank');
        }
    };

    return (
        <div className="flex flex-col gap-2 mt-2">
            <Button
                variant={type as any}
                onClick={handleClick}
                className="w-full justify-between group"
            >
                <span className="flex items-center gap-2">
                    {url.includes('login') ? <Icons.User className="w-4 h-4" /> : <Icons.ExternalLink className="w-4 h-4" />}
                    {label}
                </span>
                <Icons.ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Button>
        </div>
    );
};
