import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './styles.css';
import Loader from '../../components/Common/Loader';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Please enter both username and password.');
      return;
    }
    
    try {
      setLoading(true);
      await login(username, password);
      // AuthContext handles the navigation
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black p-4">
      {/* Login Form */}
      <motion.div className="w-full max-w-md bg-darkgrey p-8 rounded-lg shadow-lg login-container"
      initial={{opacity: 0, y: 50}} animate={{opacity: 1, y: 0}} transition={{duration: 0.5}}>
      
        <h1 className="text-2xl font-bold text-white text-center mb-6">Log In</h1>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          {/* Username Input */}
          <div className="form-group">
            <label htmlFor="username" className="block text-grey text-sm mb-2">
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              className="input-field"
            />
          </div>

          {/* Password Input */}
          <div className="form-group">
            <label htmlFor="password" className="block text-grey text-sm mb-2">
              Password
            </label>
            <div className="password-input">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                className="input-field"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="toggle-password"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {/* Login Button */}
          <button
            type="submit"
            className="submit-button"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* Create Account Link */}
        <div className="mt-6 text-center text-sm create-account">
          <span className="text-grey">Don't have an account? </span>
          <a href="/register" className="register-link">
            Create Account
          </a>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;