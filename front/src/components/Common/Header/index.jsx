import React from "react";
import './styles.css';
import TemporaryDrawer from "./drawer.jsx";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";

function Header() {
    const { isAuthenticated, loading, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/');
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    return (
        <div className="bg-black text-white flex justify-between items-center py-6 px-12 md:px-6 z-10 top-0 left-0">
            
            <h1 className="logo text-xl">CryptoSpot<span className="text-blue">.</span></h1>

            <div className="links flex justify-end gap-6 items-center">
                    <Link to="/home">Home</Link>
                    <Link to="/dashboard">Dashboard</Link>
                    <Link to="/compare">Compare</Link>
                    
                    {isAuthenticated ? (
                        <Link to="/analysis">Analysis</Link>
                    ) : (
                        <span className="disabled-link">Analysis</span>
                    )}
                    

                    
                    
                    {isAuthenticated ? (
                        <Link onClick={handleLogout} className={`cursor-pointer ${loading ? 'opacity-50' : ''}`} disabled={loading}>
                            {loading ? 'Logging out...' : 'Log Out'}
                        </Link>
                    ) : (
                        <Link to="/login">Log In</Link>
                    )}
            </div>
            <div className="mobile-drawer">
                <TemporaryDrawer isAuthenticated={isAuthenticated} />
            </div>
        </div>
    );
}

export default Header;