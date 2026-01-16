import React, { createContext, useState, useEffect, ReactNode, useContext } from 'react';
import { authAPI, setAccessToken, clearTokens, isTokenExpired, tenantsAPI } from '../services/api';
import type { LoginResponse, Tenant } from '../services/api.types';

// --- Configuration ---
// Set this to true to bypass authentication for development purposes.
// Controlled by VITE_BYPASS_AUTH environment variable
const BYPASS_AUTH_FOR_DEV = import.meta.env.VITE_BYPASS_AUTH === 'true';
// ---------------------

interface User {
  id: string;
  email: string;
  tenantId: string;
  name: string;
  role?: string;
  tenant?: Tenant;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAuthLoading: boolean;
  login: (tenantId: string, userId: string, apiKey: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (name: string, email: string, phone?: string, billingTier?: string) => Promise<void>;
  refreshToken: () => Promise<boolean>;
}

export const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  // Check auth status on initial load
  useEffect(() => {
    const checkAuth = async () => {
      if (BYPASS_AUTH_FOR_DEV) {
        // If bypassing auth, create a mock user immediately
        const mockUser: User = {
          id: 'dev-user-123',
          email: 'dev@example.com',
          tenantId: 'dev-tenant',
          name: 'Dev User',
          role: 'admin',
        };
        setUser(mockUser);
        setIsAuthLoading(false);
        return;
      }

      // Check if we have a stored user and valid token
      const storedUser = sessionStorage.getItem('user');
      if (storedUser) {
        try {
          const parsedUser = JSON.parse(storedUser);
          
          // Check if token is expired
          if (isTokenExpired()) {
            // Try to refresh token
            try {
              const response = await authAPI.refresh() as LoginResponse;
              setAccessToken(response.access_token, 1800); // 30 minutes
              setUser(parsedUser);
            } catch (error) {
              console.error('Token refresh failed:', error);
              clearTokens();
              sessionStorage.removeItem('user');
              setUser(null);
            }
          } else {
            // Token is still valid
            setUser(parsedUser);
          }
        } catch (error) {
          console.error('Failed to parse user from sessionStorage:', error);
          sessionStorage.removeItem('user');
          clearTokens();
        }
      }
      
      setIsAuthLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (tenantId: string, userId: string, apiKey: string) => {
    if (BYPASS_AUTH_FOR_DEV) {
      // In bypass mode, login just sets the mock user
      const mockUser: User = {
        id: userId || 'dev-user-123',
        email: 'dev@example.com',
        tenantId: tenantId || 'dev-tenant',
        name: 'Dev User',
        role: 'admin',
      };
      setUser(mockUser);
      sessionStorage.setItem('user', JSON.stringify(mockUser));
      return;
    }

    // Real login logic using API
    setIsAuthLoading(true);
    try {
      const response = await authAPI.login(tenantId, userId, apiKey) as LoginResponse;
      
      // Store access token (expires in 30 minutes)
      setAccessToken(response.access_token, 1800);
      
      // Fetch tenant details
      const tenant = await tenantsAPI.getCurrentTenant() as Tenant;
      
      const authenticatedUser: User = {
        id: userId,
        email: tenant.email,
        tenantId: response.tenant_id,
        name: tenant.name,
        tenant: tenant,
      };
      
      setUser(authenticatedUser);
      sessionStorage.setItem('user', JSON.stringify(authenticatedUser));
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsAuthLoading(false);
    }
  };

  const logout = async () => {
    if (BYPASS_AUTH_FOR_DEV) {
      // In bypass mode, logout clears the mock user
      setUser(null);
      sessionStorage.removeItem('user');
      return;
    }

    // Real logout logic
    setIsAuthLoading(true);
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearTokens();
      setUser(null);
      sessionStorage.removeItem('user');
      setIsAuthLoading(false);
    }
  };

  const register = async (name: string, email: string, phone?: string, billingTier: string = 'free') => {
    if (BYPASS_AUTH_FOR_DEV) {
      // In bypass mode, register also sets the mock user
      const mockUser: User = {
        id: 'dev-user-456',
        email: email,
        tenantId: 'dev-tenant-new',
        name: name,
        role: 'admin',
      };
      setUser(mockUser);
      sessionStorage.setItem('user', JSON.stringify(mockUser));
      return;
    }

    // Real registration logic
    setIsAuthLoading(true);
    try {
      const tenant = await tenantsAPI.register({
        name,
        email,
        phone,
        billing_tier: billingTier,
      }) as Tenant;

      const newUser: User = {
        id: tenant.id,
        email: tenant.email,
        tenantId: tenant.id,
        name: tenant.name,
        tenant: tenant,
      };

      setUser(newUser);
      sessionStorage.setItem('user', JSON.stringify(newUser));
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsAuthLoading(false);
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const response = await authAPI.refresh() as LoginResponse;
      setAccessToken(response.access_token, 1800);
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      clearTokens();
      setUser(null);
      sessionStorage.removeItem('user');
      return false;
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isAuthLoading,
    login,
    logout,
    register,
    refreshToken,
  };

  // Render children only when authentication loading is complete
  if (isAuthLoading) {
    return null; // Or a loading spinner component
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the AuthContext
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
