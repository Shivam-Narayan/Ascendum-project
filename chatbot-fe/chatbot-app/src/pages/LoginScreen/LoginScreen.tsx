import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  IconButton,
  InputAdornment,
  Snackbar,
  Alert,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import "./loginscreen.css";
import { loginUser } from "../../services/LoginApi";

type BackendErrorResponse = {
  detail?: string;
  [key: string]: string[] | string | undefined;
};

const LoginScreen: React.FC = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState<"success" | "error">(
    "success"
  );

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleTogglePassword = () => {
    setShowPassword((prev) => !prev);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await loginUser(formData);
      console.log("Login successful:", response);

      // Save token + user to localStorage/sessionStorage
      localStorage.setItem("token", response.token);
      localStorage.setItem("user", JSON.stringify(response.user));

      setSnackbarMessage("Login successful! Redirecting...");
      setSnackbarSeverity("success");
      setOpenSnackbar(true);

      // Redirect after short delay
      setTimeout(() => {
        navigate("/home");
      }, 2000);
    } catch (error) {
      const backendError = error as BackendErrorResponse;

      let message = "Login failed";
      if (backendError.detail) {
        message = backendError.detail;
      } else {
        const firstKey = Object.keys(backendError)[0];
        const firstError = backendError[firstKey];
        if (Array.isArray(firstError)) {
          message = firstError[0];
        } else if (typeof firstError === "string") {
          message = firstError;
        }
      }

      setSnackbarMessage(message);
      setSnackbarSeverity("error");
      setOpenSnackbar(true);
    }
  };

  return (
    <Box className="login-container">
      <Box className="login-card">
        <Typography variant="h5" className="login-title">
          Ascend AI Chatbot
        </Typography>

        <form onSubmit={handleSubmit} className="login-form">
          <TextField
            fullWidth
            label="Email"
            variant="outlined"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            className="login-input"
            required
          />

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
            fullWidth
            sx={{ mt: 2 }}
          >
            Login
          </Button>

          <Typography className="login-register-text" align="center" sx={{ mt: 2 }}>
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

      {/* Snackbar */}
      <Snackbar
        open={openSnackbar}
        autoHideDuration={3000}
        onClose={() => setOpenSnackbar(false)}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={() => setOpenSnackbar(false)}
          severity={snackbarSeverity}
          sx={{ width: "100%" }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LoginScreen;
