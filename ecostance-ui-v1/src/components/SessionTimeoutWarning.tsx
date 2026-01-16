import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './ui/Dialog';
import { Button } from './ui/Button';
import { Icons } from './icons';

interface SessionTimeoutWarningProps {
  timeUntilExpiry: number; // in seconds
  warningThreshold: number; // show warning when this many seconds remain
  onExtendSession: () => void;
  onLogout: () => void;
}

export const SessionTimeoutWarning: React.FC<SessionTimeoutWarningProps> = ({
  timeUntilExpiry,
  warningThreshold,
  onExtendSession,
  onLogout,
}) => {
  const [showWarning, setShowWarning] = useState(false);
  const [countdown, setCountdown] = useState(timeUntilExpiry);

  useEffect(() => {
    // Show warning when time remaining is below threshold
    if (timeUntilExpiry <= warningThreshold && timeUntilExpiry > 0) {
      setShowWarning(true);
      setCountdown(timeUntilExpiry);
    } else {
      setShowWarning(false);
    }
  }, [timeUntilExpiry, warningThreshold]);

  useEffect(() => {
    if (!showWarning) return;

    // Update countdown every second
    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          onLogout(); // Auto-logout when time expires
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [showWarning, onLogout]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleExtendSession = () => {
    setShowWarning(false);
    onExtendSession();
  };

  return (
    <Dialog open={showWarning} onOpenChange={setShowWarning}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <Icons.AlertTriangle className="h-6 w-6 text-yellow-500" />
            </div>
            <DialogTitle>Session Expiring Soon</DialogTitle>
          </div>
          <DialogDescription>
            Your session will expire in <span className="font-bold text-red-600">{formatTime(countdown)}</span>.
            You will be automatically logged out for security reasons.
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-4">
          <p className="text-sm text-gray-600">
            Would you like to extend your session and continue working?
          </p>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onLogout}>
            Logout Now
          </Button>
          <Button onClick={handleExtendSession}>
            <Icons.RefreshCw className="h-4 w-4 mr-2" />
            Extend Session
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
