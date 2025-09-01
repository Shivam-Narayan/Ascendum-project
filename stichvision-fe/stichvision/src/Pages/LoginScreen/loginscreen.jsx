import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  MenuItem,
  Typography,
  IconButton,
  InputAdornment,
  Snackbar,
  Alert,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import "./loginscreen.css";
import { loginUser } from "../../Services/LoginApi";

const LoginScreen = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    identifier: "",
    line_number: "",
    department: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await loginUser(formData);

      // Handle successful login
      setSuccess("Login successful! Redirecting...");

      // Store token and user data in localStorage
      localStorage.setItem("token", response.token);
      localStorage.setItem("user", JSON.stringify(response.user));

      // Redirect to dashboard after a delay
      setTimeout(() => {
        navigate("/dashboard");
      }, 1500);
    } catch (err) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setError("");
    setSuccess("");
  };

  return (
    <Box className="login-container">
      <Box className="login-card">
        <Typography variant="h5" className="login-title">
          Welcome to Seam Guard
        </Typography>
        <form onSubmit={handleSubmit} className="login-form">
          <TextField
            fullWidth
            label="Emp ID / Email / Phone"
            variant="outlined"
            name="identifier"
            value={formData.identifier}
            onChange={handleChange}
            className="login-input"
            required
          />

          <TextField
            fullWidth
            select
            label="Line"
            variant="outlined"
            name="line_number"
            value={formData.line_number}
            onChange={handleChange}
            className="login-input"
            required
          >
            {[...Array(15)].map((_, i) => (
              <MenuItem key={i + 1} value={`L${i + 1}`}>{`Line ${
                i + 1
              }`}</MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            select
            label="Department"
            variant="outlined"
            name="department"
            value={formData.department}
            onChange={handleChange}
            className="login-input"
            required
          >
            {["Production", "QA", "Maintenance", "Logistics", "HR"].map(
              (dep) => (
                <MenuItem key={dep} value={dep}>
                  {dep}
                </MenuItem>
              )
            )}
          </TextField>

          <TextField
            fullWidth
            label="Password"
            variant="outlined"
            type={showPassword ? "text" : "password"}
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
            {loading ? "Logging in..." : "Login"}
          </Button>

          <Typography className="login-register-text" align="center">
            Admin?{" "}
            <Button
              variant="text"
              onClick={() => navigate("/admin/login")}
              className="login-register-button"
            >
              Admin Login
            </Button>
            <br /> {/* Forces new line */}
            Not registered?{" "}
            <Button
              variant="text"
              onClick={() => navigate("/register")}
              className="login-register-button"
            >
              Register
            </Button>
          </Typography>
        </form>
      </Box>

      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity="error"
          sx={{ width: "100%" }}
        >
          {error}
        </Alert>
      </Snackbar>

      {/* Success Snackbar */}
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity="success"
          sx={{ width: "100%" }}
        >
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LoginScreen;
