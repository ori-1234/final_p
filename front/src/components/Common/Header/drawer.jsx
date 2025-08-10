import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import {IconButton} from '@mui/material';
import MenuRounded from '@mui/icons-material/MenuRounded';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';

export default function AnchorTemporaryDrawer() {
  const [open, setOpen] = useState(false);
  const { isAuthenticated, loading, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      setOpen(false);
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <div>
        <IconButton onClick={() => setOpen(true)}>
          <MenuRounded className="text-white" />
        </IconButton>
        <Drawer 
          anchor={'right'} 
          open={open} 
          onClose={() => setOpen(false)}
          PaperProps={{
            sx: {
              backgroundColor: "black",
              color: "white"
            }
          }}
        >
          <div className="flex flex-col gap-6 items-start h-full w-60 py-6 px-6">
            <Link to="/home" onClick={() => setOpen(false)}>Home</Link>
            <Link to="/dashboard" onClick={() => setOpen(false)}>Dashboard</Link>
            <Link to="/compare" onClick={() => setOpen(false)}>Compare</Link>
            
            {isAuthenticated ? (
                <Link to="/analysis" onClick={() => setOpen(false)}>Analysis</Link>
            ) : (
                <span className="disabled-link">Analysis</span>
            )}



            {isAuthenticated ? (
                <Link 
                  onClick={handleLogout} 
                  className={`cursor-pointer ${loading ? 'opacity-50' : ''}`} 
                  disabled={loading}
                >
                  {loading ? 'Logging out...' : 'Log Out'}
                </Link>
            ) : (
                <Link to="/login" onClick={() => setOpen(false)}>Log In</Link>
            )}
          </div>
        </Drawer>
    </div>
  );
}
