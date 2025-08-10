import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../functions/auth';
import { useNavigate, useLocation } from 'react-router-dom';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    // Only check authentication for protected routes
    useEffect(() => {
        const path = location.pathname;
        // Only check auth for exchange and profile routes
        if (path.startsWith('/exchange') || path.startsWith('/profile')) {
            checkAuth();
        }
    }, [location.pathname]);

    const checkAuth = async () => {
        try {
            const { isAuthenticated } = await authAPI.authenticated_user();
            setIsAuthenticated(isAuthenticated);
            if (!isAuthenticated) {
                // Save the attempted URL to redirect back after login
                navigate('/login', { state: { from: location.pathname } });
            }
        } catch (error) {
            setIsAuthenticated(false);
            navigate('/login', { state: { from: location.pathname } });
        }
    };

    const register = async (userData) => {
        try {
            setLoading(true);
            setError(null);
            await authAPI.register(userData);
            // After successful registration, automatically log them in
            await login(userData.username, userData.password);
        } catch (error) {
            setError(error.response?.data?.message || error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const login = async (username, password) => {
        try {
            setLoading(true);
            setError(null);
            await authAPI.login(username, password);
            setIsAuthenticated(true);
            
            // Get the redirect path from location state or default to dashboard
            const from = location.state?.from || '/dashboard';
            navigate(from);
        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            setLoading(true);
            await authAPI.logout();
            setIsAuthenticated(false);
            navigate('/');
        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const clearError = () => {
        setError(null);
    };

    const value = {
        isAuthenticated,
        loading,
        error,
        login,
        logout,
        register,
        clearError
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 