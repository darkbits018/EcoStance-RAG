import { useState, useEffect, useCallback } from 'react';
import { authAPI, setAccessToken, clearTokens, isTokenExpired } from '../services/api';
import type { LoginResponse } from '../services/api.types';

interface UseAuthReturn {
  isAuthenticated: boolean;
  loading: boolean;
  error: Error | null;
  login: (tenantId: string, userId: string, apiKey: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
}

export function useAuth(): UseAuthReturn {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (isTokenExpired()) {
          // Try to refresh token
          const refreshed = await refreshToken();
          setIsAuthenticated(refreshed);
        } else {
          // Verify current token
          await authAPI.verify();
          setIsAuthenticated(true);
        }
      } catch (err) {
        setIsAuthenticated(false);
        clearTokens();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = useCallback(async (tenantId: string, userId: string, apiKey: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authAPI.login(tenantId, userId, apiKey) as LoginResponse;
      
      // Store access token (expires_in is typically 1800 seconds = 30 minutes)
      setAccessToken(response.access_token, 1800);
      
      setIsAuthenticated(true);
      return true;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Login failed');
      setError(error);
      setIsAuthenticated(false);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      clearTokens();
      setIsAuthenticated(false);
    }
  }, []);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const response = await authAPI.refresh() as LoginResponse;
      setAccessToken(response.access_token, 1800);
      setIsAuthenticated(true);
      return true;
    } catch (err) {
      clearTokens();
      setIsAuthenticated(false);
      return false;
    }
  }, []);

  return {
    isAuthenticated,
    loading,
    error,
    login,
    logout,
    refreshToken,
  };
}
