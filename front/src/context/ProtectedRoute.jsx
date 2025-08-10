import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { authAPI } from '../functions/auth';
import Loader from '../components/Common/Loader';

const ProtectedRoute = ({ children }) => {
  const [authStatus, setAuthStatus] = useState({ checked: false, isAuthenticated: false });
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Always make the API call since HTTP-only cookies can't be detected by JavaScript
        // The server will check if the cookie exists
        await authAPI.authenticated_user();
        setAuthStatus({ checked: true, isAuthenticated: true });
      } catch (error) {
        // Don't log 401 errors as they're expected when not authenticated
        if (error?.response?.status !== 401) {
          console.error('Auth check error in ProtectedRoute:', error);
        }
        setAuthStatus({ checked: true, isAuthenticated: false });
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
    
    // This effect should only run once per mount
  }, []);
  
  if (isLoading) {
    return <Loader />;
  }
  
  if (!authStatus.isAuthenticated) {
    // Save the attempted URL for redirecting after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // Render children if authenticated
  return children;
};

export default ProtectedRoute; 