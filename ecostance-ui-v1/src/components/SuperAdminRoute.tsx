import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.v2';
import { Icons } from './icons';

interface SuperAdminRouteProps {
  children: React.ReactNode;
}

export const SuperAdminRoute: React.FC<SuperAdminRouteProps> = ({ children }) => {
  const { user, isAuthLoading } = useAuth();

  if (isAuthLoading) {
    return (
      <div className="flex justify-center items-center h-screen w-full">
        <Icons.Spinner className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  // Check if user is authenticated and has super admin role
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== 'super_admin' && user.role !== 'admin') {
    // Redirect to dashboard with error message
    return (
      <Navigate 
        to="/" 
        replace 
        state={{ error: 'Access denied. Super admin privileges required.' }} 
      />
    );
  }

  return <>{children}</>;
};
