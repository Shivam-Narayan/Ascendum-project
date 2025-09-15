import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from "../../services/RegisterApi";
import { Leaf, Eye, EyeOff, AlertCircle } from 'lucide-react';
import './Register.css';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [generalError, setGeneralError] = useState('');
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  const navigate = useNavigate();

  // Check if all required fields are filled
  const isFormValid = name.trim() !== '' && 
                     email.trim() !== '' && 
                     password.trim() !== '' && 
                     confirmPassword.trim() !== '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setGeneralError('');

    // Client-side validation
    if (password !== confirmPassword) {
      setErrors({ confirm_password: ['Passwords do not match'] });
      return;
    }

    if (password.length < 6) {
      setErrors({ password: ['Password must be at least 6 characters long'] });
      return;
    }

    setLoading(true);

    try {
      const response = await registerUser({ name, email, password, confirmPassword });
      
      setSnackbar({
        open: true,
        message: response.message || 'Registration successful!',
        severity: 'success',
      });
      
      // Redirect to login after successful registration
      setTimeout(() => navigate('/login'), 2000);
      
    } catch (error) {
      if (typeof error === 'object' && error.constructor === Object) {
        // Handle field-specific validation errors from backend
        setErrors(error);
      } else {
        // Handle general errors
        setSnackbar({
          open: true,
          message: error.message || 'Registration failed. Please try again.',
          severity: 'error',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <div className="register-container">
      <div className="register-wrapper">
        {/* Header */}
        <div className="header">
          <div className="header-content">
            <Leaf className="leaf-icon" />
            <h2 className="main-title">AI Assistant for Plant and Soil</h2>
          </div>
        </div>

        {/* Register Form */}
        <div className="form-container">
          <h2 className="form-title">Create Your Account</h2>
          
          {generalError && (
            <div className="error-message">
              <AlertCircle size={18} />
              <span className="error-text">{generalError}</span>
            </div>
          )}

          {/* Snackbar for notifications */}
          {snackbar.open && (
            <div className={`snackbar snackbar-${snackbar.severity}`}>
              <span>{snackbar.message}</span>
              <button onClick={handleCloseSnackbar} className="snackbar-close">×</button>
            </div>
          )}

          <form onSubmit={handleSubmit} className="form">
            {/* Full Name */}
            <div className="form-group">
              <label htmlFor="name" className="form-label">
                Full Name
              </label>
              <input
                id="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="form-input"
                placeholder="Enter your full name"
              />
              {errors.name && (
                <p className="error-text">{Array.isArray(errors.name) ? errors.name[0] : errors.name}</p>
              )}
            </div>

            {/* Email */}
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="form-input"
                placeholder="Enter your email"
              />
              {errors.email && (
                <p className="error-text">{Array.isArray(errors.email) ? errors.email[0] : errors.email}</p>
              )}
            </div>

            {/* Password */}
            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className="password-container">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="password-input"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="password-toggle"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && (
                <p className="error-text">{Array.isArray(errors.password) ? errors.password[0] : errors.password}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">
                Confirm Password
              </label>
              <div className="password-container">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="password-input"
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="password-toggle"
                >
                  {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.confirm_password && (
                <p className="error-text">{Array.isArray(errors.confirm_password) ? errors.confirm_password[0] : errors.confirm_password}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || !isFormValid}
              className="submit-button"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          {/* Login Link */}
          <div className="login-link">
            <p className="login-text">
              Have an account?{' '}
              <Link to="/login" className="login-link-text">
                Login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;