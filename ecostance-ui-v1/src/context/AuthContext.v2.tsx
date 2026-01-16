import React, { createContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
import { authAPI, setAccessToken, clearTokens, getTimeUntilExpiry, isTokenExpired } from '../services/api';
import { SessionTimeoutWarning } from '../components/SessionTimeoutWarning';

// --- Configuration ---
const BYPASS_AUTH_FOR_DEV = import.meta.env.VITE_BYPASS_AUTH === 'true';
const TOKEN_REFRESH_INTERVAL = 25 * 60 * 1000; // Refresh every 25 minutes (before 30 min expiry)
const SESSION_WARNING_THRESHOLD = 5 * 60; // Show warning 5 minutes before expiry
// ---------------------

interface User {
  id: string;
  email: string;
  tenantId: string;
  role?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAuthLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string, tenantId: string) => Promise<void>;
  refreshSession: () => Promise<void>;
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
      const { access_token, expires_in, tenant_id } = response as {
        access_token: string;
        expires_in: number;
        tenant_id?: string;
      };
      
      setAccessToken(access_token, expires_in);
      
      // Update user if tenant_id is returned
      if (tenant_id && user) {
        setUser({ ...user, tenantId: tenant_id });
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
        };
        setUser(mockUser);
        setIsAuthLoading(false);
        return;
      }

      try {
        // Try to refresh the session using the httpOnly cookie
        // This will work even if the access token in memory is lost
        const response = await authAPI.refresh() as {
          access_token: string;
          expires_in: number;
          tenant_id?: string;
          user_id?: string;
          email?: string;
        };
        
        if (response.access_token) {
          // Store the new access token
          setAccessToken(response.access_token, response.expires_in);
          
          // Set user data
          const userData: User = {
            id: response.user_id || 'user',
            email: response.email || '',
            tenantId: response.tenant_id || '',
          };
          setUser(userData);
          setupTokenRefresh();
        }
      } catch (error) {
        console.log('No valid session found, redirecting to login');
        clearTokens();
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
      };
      setUser(mockUser);
      // Set a mock token for API calls
      setAccessToken('dev-mock-token', 86400); // 24 hours
      return;
    }

    setIsAuthLoading(true);
    try {
      const response = await authAPI.login(email, password);
      const { access_token, expires_in, tenant_id, user_id } = response as {
        access_token: string;
        expires_in: number;
        tenant_id?: string;
        user_id?: string;
      };

      // Store access token in memory
      setAccessToken(access_token, expires_in);

      // Refresh token is automatically stored in httpOnly cookie by backend
      
      // Set user data
      const userData: User = {
        id: user_id || email,
        email: email,
        tenantId: tenant_id || '',
      };
      setUser(userData);

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
