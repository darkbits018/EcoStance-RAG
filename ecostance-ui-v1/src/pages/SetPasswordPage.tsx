import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { Icons } from '../components/icons';
import { authAPI } from '../services/api';

const SetPasswordPage: React.FC = () => {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<boolean>(false);
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    const searchParams = new URLSearchParams(location.search);
    const token = searchParams.get('invite_token');

    useEffect(() => {
        if (!token) {
            navigate('/login');
        }
    }, [token, navigate]);

    if (!token) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (password !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        if (password.length < 8) {
            setError("Password must be at least 8 characters");
            return;
        }

        setIsLoading(true);
        try {
            await authAPI.setPassword(token, password);
            setSuccess(true);
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (error: any) {
            console.error("Set password failed:", error);
            setError(error.message || "Failed to set password. Link might be expired.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4">
            <div className="w-full max-w-md space-y-6">
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-primary">Set Your Password</h1>
                    <p className="text-sm text-text-secondary">Welcome to the platform! Please set a password for your new account.</p>
                </div>

                {success ? (
                    <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-6 rounded text-center">
                        <Icons.CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-500" />
                        <h3 className="text-lg font-medium">Password Set Successfully!</h3>
                        <p className="mt-2">Redirecting to login...</p>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
                                <span className="block sm:inline">{error}</span>
                            </div>
                        )}

                        <div>
                            <Label htmlFor="password">New Password</Label>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    disabled={isLoading}
                                    className="pr-10"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                >
                                    {showPassword ? (
                                        <Icons.EyeOff className="h-4 w-4" />
                                    ) : (
                                        <Icons.Eye className="h-4 w-4" />
                                    )}
                                </button>
                            </div>
                        </div>

                        <div>
                            <Label htmlFor="confirmPassword">Confirm Password</Label>
                            <Input
                                id="confirmPassword"
                                type="password"
                                placeholder="••••••••"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                disabled={isLoading}
                            />
                        </div>

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? (
                                <>
                                    <Icons.Spinner className="h-4 w-4 animate-spin mr-2" />
                                    Setting Password...
                                </>
                            ) : (
                                'Set Password & Login'
                            )}
                        </Button>

                        <div className="text-center mt-4">
                            <Button
                                type="button"
                                variant="ghost"
                                onClick={() => navigate('/login')}
                            >
                                Back to Login
                            </Button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default SetPasswordPage;
