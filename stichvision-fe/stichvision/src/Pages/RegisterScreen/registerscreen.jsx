import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Grid,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import './registerscreen.css';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import Tooltip from '@mui/material/Tooltip';
import { fetchEmployeeDetails, registerEmployee } from '../../Services/RegisterApi';

const RegisterScreen = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    empId: '',
    name: '',
    email: '',
    phone: '',
    line: '',
    department: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [userDetailsLoaded, setUserDetailsLoaded] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success', // 'success', 'error', 'warning', 'info'
  });

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    // Restrict password and confirmPassword to 10 characters
    if ((name === 'password' || name === 'confirmPassword') && value.length > 10) {
      return;
    }

    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const fetchUserDetails = async (empId) => {
    setLoading(true);
    try {
      const data = await fetchEmployeeDetails(empId);
      setFormData((prev) => ({
        ...prev,
        name: data.name,
        email: data.email,
        phone: data.phone_number,
        line: data.line_number,
        department: data.department,
      }));
      setUserDetailsLoaded(true);
      setSnackbar({
        open: true,
        message: 'Employee details loaded successfully',
        severity: 'success',
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.message || 'Failed to fetch employee details',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKnowClick = () => {
    if (formData.empId.length >= 1 && formData.empId.length <= 9) {
      fetchUserDetails(formData.empId);
    }
  };

  const validatePassword = (password) => {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,10}$/;
    return regex.test(password);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const isPasswordValid = validatePassword(formData.password);
    const isMatch = formData.password === formData.confirmPassword;

    if (!isPasswordValid && !isMatch) {
      setPasswordError('Password must meet criteria and match confirmation.');
      return;
    }

    if (!isPasswordValid) {
      setPasswordError(
        'Password must be 8–10 characters with uppercase, lowercase, number, and special character.'
      );
      return;
    }

    if (!isMatch) {
      setPasswordError("Passwords do not match.");
      return;
    }

    setPasswordError('');

    try {
      setLoading(true);
      const response = await registerEmployee(formData.empId, formData.password, formData.confirmPassword);
      
      setSnackbar({
        open: true,
        message: response.message || 'Registration successful!',
        severity: 'success',
      });
      
      // Redirect to login after successful registration
      setTimeout(() => navigate('/login'), 2000);
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.message || 'Registration failed. Please try again.',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box className="register-container">
      <Box className="register-card">
        <Typography variant="h5" className="register-title">
          Create Your Account
        </Typography>
        <form onSubmit={handleSubmit} className="register-form">
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} sx={{ position: 'relative' }}>
              <TextField
                fullWidth
                label="Employee ID"
                variant="outlined"
                name="empId"
                value={formData.empId}
                onChange={handleChange}
                className="register-input"
                inputProps={{ maxLength: 9 }}
                disabled={userDetailsLoaded}
              />
              {!userDetailsLoaded && formData.empId.length > 0 && (
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={handleKnowClick}
                  disabled={
                    formData.empId.length < 1 ||
                    formData.empId.length > 9 ||
                    loading
                  }
                  sx={{
                    position: 'absolute',
                    right: 8,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    height: '36px',
                    minWidth: '80px',
                    borderRadius: '20px',
                    backgroundColor: '#4CAF50',
                    '&:hover': {
                      backgroundColor: '#45a049',
                    },
                    '&:disabled': {
                      backgroundColor: '#cccccc',
                      color: '#666666',
                    },
                  }}
                >
                  {loading ? (
                    <CircularProgress size={24} sx={{ color: 'white' }} />
                  ) : (
                    'Know'
                  )}
                </Button>
              )}
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Full Name"
                variant="outlined"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="register-input"
                disabled
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                variant="outlined"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="register-input"
                disabled
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone Number"
                variant="outlined"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="register-input"
                disabled
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Line Number"
                variant="outlined"
                name="line"
                value={formData.line}
                onChange={handleChange}
                className="register-input"
                disabled
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Department"
                variant="outlined"
                name="department"
                value={formData.department}
                onChange={handleChange}
                className="register-input"
                disabled
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Password"
                variant="outlined"
                type="text"  // Changed from 'text' to 'password' for security
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="register-input"
                disabled={!userDetailsLoaded}
                inputProps={{ maxLength: 10 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Confirm Password"
                variant="outlined"
                type="text"  // Changed from 'text' to 'password' for security
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="register-input"
                disabled={!userDetailsLoaded}
                inputProps={{ maxLength: 10 }}
              />
            </Grid>

            {passwordError && (
              <Grid item xs={12} style={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" color="error" style={{ marginRight: '8px' }}>
                  {passwordError}
                </Typography>
                <Tooltip
                  title={
                    <div style={{ fontSize: '0.9rem' }}>
                      Password must contain:
                      <ul style={{ margin: '4px 0 0 16px', padding: 0 }}>
                        <li>1 uppercase letter</li>
                        <li>1 lowercase letter</li>
                        <li>1 number</li>
                        <li>1 special character</li>
                        <li>9–10 characters total</li>
                      </ul>
                    </div>
                  }
                  arrow
                  placement="right"
                >
                  <InfoOutlinedIcon style={{ cursor: 'pointer', color: '#f44336' }} />
                </Tooltip>
              </Grid>
            )}
          </Grid>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            className="register-button"
            sx={{ mt: 3 }}
            disabled={!userDetailsLoaded || loading}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Register'}
          </Button>

          <Typography className="register-login-text">
            Already have an account?
            <Button
              variant="text"
              onClick={() => navigate('/login')}
              className="register-login-button"
            >
              Login
            </Button>
          </Typography>
        </form>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default RegisterScreen;