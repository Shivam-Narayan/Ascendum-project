import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Snackbar,
  Alert,
  IconButton,
  InputAdornment
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom'; 
import { adminLogin } from '../../Services/AdminLoginApi';
import './loginscreen.css';

const AdminLoginScreen = () => {
  const [formData, setFormData] = useState({
    emp_id: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

  try {
    const response = await adminLogin(formData);
    setSuccess("Admin login successful!");
    localStorage.setItem("adminToken", response.token);
    localStorage.setItem("adminUser", JSON.stringify({ emp_id: response.emp_id }));
    navigate("/admin/AdminDashboard");
    } catch (err) {
    setError(err.message || "Login failed. Please try again.");
    } finally {
    setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setError('');
    setSuccess('');
  };

  return (
    <Box className="login-container">
      <Box className="login-card">
        <Typography variant="h5" className="login-title">Admin Login</Typography>
        <form onSubmit={handleSubmit} className="login-form">
          <TextField
            fullWidth
            label="Emp ID"
            variant="outlined"
            name="emp_id"
            value={formData.emp_id}
            onChange={handleChange}
            className="login-input"
            required
          />

          <TextField
            fullWidth
            label="Password"
            variant="outlined"
            type={showPassword ? 'text' : 'password'}
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="login-input"
            required
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={handleTogglePassword} edge="end">
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Button
            type="submit"
            variant="contained"
            color="primary"
            className="login-button"
            disabled={loading}
            fullWidth
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <Typography variant="body2" align="center" sx={{ marginTop: 2 }}>
          Not an admin?{' '}
          <Button
            variant="text"
            onClick={() => navigate('/login')}
            className="login-register-button"
          >
            Back to User Login
          </Button>
        </Typography>
      </Box>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AdminLoginScreen;
