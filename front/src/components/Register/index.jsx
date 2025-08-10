import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './styles.css';
import Loader from '../../components/Common/Loader';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { register, error: authError, clearError } = useAuth();

  useEffect(() => {
    // Clear any previous auth errors when component mounts
    clearError();
    // Clear error when component unmounts
    return () => clearError();
  }, [clearError]);

  useEffect(() => {
    // Update local error state when auth error changes
    if (authError) {
      setError(authError);
    }
  }, [authError]);

  const handleChange = (e) => {
    setError(''); // Clear errors on input change
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validateForm = () => {
    if (!formData.email.includes('@')) {
      setError('Please enter a valid email address');
      return false;
    }
    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters long');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    return true;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }
    
    try {
      setLoading(true);
      // Create registration data without confirmPassword
      const registrationData = {
        email: formData.email,
        username: formData.username,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone_number: formData.phone_number || null,
        password: formData.password
      };
      await register(registrationData);
      // AuthContext handles the navigation after successful registration
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.message || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-black p-4 register-container">
      <motion.div 
        className="w-full max-w-md bg-darkgrey p-8 rounded-lg shadow-lg login-container"
        initial={{opacity: 0, y: 50}} 
        animate={{opacity: 1, y: 0}} 
        transition={{duration: 0.5}}
      >
        <h1 className="text-2xl font-bold text-white mb-8 text-center">Create Account</h1>
        
        {error && (
          <motion.div 
            className="error-message"
            initial={{opacity: 0}}
            animate={{opacity: 1}}
            transition={{duration: 0.3}}
          >
            {error.split('\n').map((err, index) => (
              <p key={index}>{err}</p>
            ))}
          </motion.div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="form-group">
            <label className="block text-grey text-sm mb-2">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              className="input-field"
              required
            />
          </div>

          <div className="form-group">
            <label className="block text-grey text-sm mb-2">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              className="input-field"
              required
              minLength={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="form-group">
              <label className="block text-grey text-sm mb-2">First Name</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="First name"
                className="input-field"
                required
              />
            </div>
            <div className="form-group">
              <label className="block text-grey text-sm mb-2">Last Name</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Last name"
                className="input-field"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="block text-grey text-sm mb-2">Phone Number (Optional)</label>
            <input
              type="tel"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              placeholder="Enter your phone number"
              className="input-field"
              pattern="[0-9]*"
            />
          </div>

          <div className="form-group">
            <label className="block text-grey text-sm mb-2">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create password"
                className="input-field"
                required
                minLength={8}
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

          <div className="form-group">
            <label className="block text-grey text-sm mb-2">Confirm Password</label>
            <div className="relative">
              <input
                type={showConfirmPassword ? "text" : "password"}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm password"
                className="input-field"
                required
                minLength={8}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="toggle-password"
              >
                {showConfirmPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="submit-button"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center text-grey text-sm">
          Already have an account?{' '}
          <Link to="/login" className="text-blue hover:text-blue/80 transition-colors">
            Log In
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default Register;