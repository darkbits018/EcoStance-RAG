import React, { createContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
import { authAPI, tenantsAPI, setAccessToken, clearTokens, getTimeUntilExpiry, isTokenExpired } from '../services/api';
import { SessionTimeoutWarning } from '../components/SessionTimeoutWarning';

// --- Configuration ---
const BYPASS_AUTH_FOR_DEV = import.meta.env.VITE_BYPASS_AUTH === 'true';
const TOKEN_REFRESH_INTERVAL = 25 * 60 * 1000; // Refresh every 25 minutes (before 30 min expiry)
const SESSION_WARNING_THRESHOLD = 5 * 60; // Show warning 5 minutes before expiry
// ---------------------

export interface User {
  id: string;
  email: string;
  tenantId: string;
  role?: string;
  billingTier?: string;
  trialEndsAt?: string | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAuthLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string, tenantId: string) => Promise<void>;
  refreshSession: () => Promise<void>;
  billingStatus?: string;
  trialEndsAt?: string | null;
  billingTier?: string;
  updateUser: (user: User | null) => void;
}

export const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [timeUntilExpiry, setTimeUntilExpiry] = useState<number>(0);

  const refreshIntervalRef = useRef<number | null>(null);
  const expiryCheckIntervalRef = useRef<number | null>(null);

  // Clear all intervals
  const clearIntervals = useCallback(() => {
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
      refreshIntervalRef.current = null;
    }
    if (expiryCheckIntervalRef.current) {
      clearInterval(expiryCheckIntervalRef.current);
      expiryCheckIntervalRef.current = null;
    }
  }, []);

  // Refresh the access token
  const refreshSession = useCallback(async () => {
    try {
      const response = await authAPI.refresh();
      const { access_token, expires_in, tenant_id, role } = response as {
        access_token: string;
        expires_in: number;
        tenant_id?: string;
        role?: string;
      };

      setAccessToken(access_token, expires_in);

      // Update user if tenant_id is returned
      if (tenant_id && user) {
        setUser({ ...user, tenantId: tenant_id, role: role || user.role });
      }

      console.log('Token refreshed successfully');
    } catch (error) {
      console.error('Failed to refresh token:', error);
      // If refresh fails, logout the user
      await logout();
    }
  }, [user]);

  // Setup automatic token refresh
  const setupTokenRefresh = useCallback(() => {
    clearIntervals();

    // Refresh token periodically
    refreshIntervalRef.current = setInterval(() => {
      if (!isTokenExpired()) {
        refreshSession();
      }
    }, TOKEN_REFRESH_INTERVAL);

    // Check expiry time every second for warning display
    expiryCheckIntervalRef.current = setInterval(() => {
      const timeRemaining = getTimeUntilExpiry();
      setTimeUntilExpiry(timeRemaining);

      // Auto-logout if token expired (handled by the warning component)
    }, 1000);
  }, [refreshSession, clearIntervals]);

  // Verify existing session on mount
  useEffect(() => {
    const verifySession = async () => {
      if (BYPASS_AUTH_FOR_DEV) {
        // Development mode - create mock user
        const mockUser: User = {
          id: 'dev-user-123',
          email: 'dev@example.com',
          tenantId: 'dev-tenant',
          role: 'admin',
          billingTier: 'free',
          trialEndsAt: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
        };
        setUser(mockUser);
        setIsAuthLoading(false);
        return;
      }

      try {
        // Try to refresh the session using the httpOnly cookie
        const response = await authAPI.refresh() as any;

        if (response.access_token) {
          // Fetch full tenant info for trial status
          try {
            const tenantData = await tenantsAPI.getCurrentTenant() as any;
            const userData: User = {
              id: response.user_id || response.user?.id || 'user',
              email: response.email || response.user?.email || '',
              tenantId: response.tenant_id || response.user?.tenant_id || '',
              role: response.role || response.user?.role,
              billingTier: tenantData.billing_tier || tenantData.billingTier,
              trialEndsAt: tenantData.trial_ends_at || tenantData.trialEndsAt,
            };
            console.log('✅ AuthContext: User session verified with trial data:', {
              tier: userData.billingTier,
              expires: userData.trialEndsAt
            });
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
          } catch (tenantErr) {
            console.error('❌ AuthContext: Failed to fetch initial tenant data:', tenantErr);
            const userData: User = {
              id: response.user_id || response.user?.id || 'user',
              email: response.email || response.user?.email || '',
              tenantId: response.tenant_id || response.user?.tenant_id || '',
              role: response.role || response.user?.role,
            };
            setUser(userData);
          }
          setupTokenRefresh();
        }
      } catch (error) {
        console.log('ℹ️ AuthContext: Session refresh failed, checking local storage...');
        // Fallback: Check if we have a valid-looking session in localStorage
        const storedUser = localStorage.getItem('user');
        const storedToken = localStorage.getItem('access_token');

        if (storedUser && storedToken) {
          try {
            const userData = JSON.parse(storedUser);
            setUser(userData);
            setAccessToken(storedToken); // Restore memory token
            console.log('Restored session from localStorage');
          } catch (e) {
            console.error('Failed to restore local session:', e);
            clearTokens();
          }
        } else {
          clearTokens();
        }
      } finally {
        setIsAuthLoading(false);
      }
    };

    verifySession();

    // Cleanup on unmount
    return () => {
      clearIntervals();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  const login = async (email: string, password: string) => {
    if (BYPASS_AUTH_FOR_DEV) {
      // Development mode
      const mockUser: User = {
        id: 'dev-user-123',
        email: email || 'dev@example.com',
        tenantId: 'dev-tenant',
        role: 'admin',
        billingTier: 'free',
        trialEndsAt: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
      };
      setUser(mockUser);
      // Set a mock token for API calls
      setAccessToken('dev-mock-token', 86400); // 24 hours
      return;
    }

    setIsAuthLoading(true);
    try {
      const response = await authAPI.login(email, password);
      const { access_token, expires_in, tenant_id, user_id, role } = response as {
        access_token: string;
        expires_in: number;
        tenant_id?: string;
        user_id?: string;
        role?: string;
      };

      // Store access token in memory and local storage via helper
      setAccessToken(access_token, expires_in);

      // Refresh token is automatically stored in httpOnly cookie by backend

      // Fetch full tenant info for trial status
      const tenantData = await tenantsAPI.getCurrentTenant() as any;

      // Set user data
      const userData: User = {
        id: user_id || email,
        email: email,
        tenantId: tenant_id || '',
        role: role,
        billingTier: tenantData.billing_tier || tenantData.billingTier,
        trialEndsAt: tenantData.trial_ends_at || tenantData.trialEndsAt,
      };

      console.log('✅ AuthContext: Login successful with trial data:', {
        tier: userData.billingTier,
        expires: userData.trialEndsAt
      });

      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));

      // Setup automatic token refresh
      setupTokenRefresh();
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsAuthLoading(false);
    }
  };

  const logout = async () => {
    if (BYPASS_AUTH_FOR_DEV) {
      setUser(null);
      return;
    }

    setIsAuthLoading(true);
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearTokens();
      clearIntervals();
      setUser(null);
      setIsAuthLoading(false);
    }
  };

  const register = async (email: string, _password: string, tenantId: string) => {
    if (BYPASS_AUTH_FOR_DEV) {
      const mockUser: User = {
        id: 'dev-user-456',
        email: email,
        tenantId: tenantId,
        role: 'user',
      };
      setUser(mockUser);
      return;
    }

    setIsAuthLoading(true);
    try {
      // Call registration API
      // After successful registration, automatically log in
      // This is a placeholder - adjust based on your API
      const mockUser: User = {
        id: 'user-456',
        email: email,
        tenantId: tenantId,
      };
      setUser(mockUser);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsAuthLoading(false);
    }
  };

  const handleExtendSession = async () => {
    await refreshSession();
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isAuthLoading,
    login,
    logout,
    register,
    refreshSession,
    billingTier: user?.billingTier,
    trialEndsAt: user?.trialEndsAt,
    updateUser: (newUser: User | null) => {
      setUser(newUser);
      if (newUser) {
        localStorage.setItem('user', JSON.stringify(newUser));
      } else {
        localStorage.removeItem('user');
      }
    },
  };

  if (isAuthLoading) {
    return (
      <div className="flex justify-center items-center h-screen w-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
      {user && !BYPASS_AUTH_FOR_DEV && (
        <SessionTimeoutWarning
          timeUntilExpiry={timeUntilExpiry}
          warningThreshold={SESSION_WARNING_THRESHOLD}
          onExtendSession={handleExtendSession}
          onLogout={logout}
        />
      )}
    </AuthContext.Provider>
  );
};

// Custom hook to use the AuthContext
export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
