import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  InputAdornment,
  IconButton,
  Snackbar,
  Alert,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import "./registerscreen.css";
import { registerUser } from "../../services/RegisterApi";
import { CircularProgress } from "@mui/material";

type BackendErrorResponse = {
  detail?: string;
  [key: string]: string[] | string | undefined;
};

const RegisterScreen: React.FC = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState<boolean>(false);
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [loading, setLoading] = useState(false);

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

  const handleToggleConfirmPassword = () => {
    setShowConfirmPassword((prev) => !prev);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await registerUser(formData);
      console.log("User registered successfully:", response);

      setSnackbarMessage("Registration successful! Redirecting to login...");
      setSnackbarSeverity("success");
      setOpenSnackbar(true);

      // Reset form
      setFormData({
        fullName: "",
        email: "",
        password: "",
        confirmPassword: "",
      });

      // Redirect after short delay
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (error) {
      const backendError = error as BackendErrorResponse;

      let message = "Registration failed";

      if (backendError.detail) {
        // Case: { "detail": "Some error" }
        message = backendError.detail;
      } else {
        // Case: { email: ["user with this email already exists."] }
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
          <TextField
            fullWidth
            label="Full Name"
            variant="outlined"
            name="fullName"
            value={formData.fullName}
            onChange={handleChange}
            className="register-input"
            required
            margin="normal"
            autoComplete="new-fullname"
          />

          <TextField
            fullWidth
            label="Email"
            variant="outlined"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="register-input"
            required
            margin="normal"
            autoComplete="new-email"
          />

          <TextField
            fullWidth
            label="Password"
            variant="outlined"
            type={showPassword ? "text" : "password"}
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="register-input"
            required
            margin="normal"
            autoComplete="new-password"
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

          <TextField
            fullWidth
            label="Confirm Password"
            variant="outlined"
            type={showConfirmPassword ? "text" : "password"}
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            className="register-input"
            required
            margin="normal"
            autoComplete="new-password"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={handleToggleConfirmPassword} edge="end">
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Button
            type="submit"
            variant="contained"
            fullWidth
            sx={{
              mt: 2,
              width: "100%",
              maxWidth: 460,
              height: 50,
              borderRadius: "20px",
              background: "linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)",
              color: "white",
              fontWeight: 600,
              fontSize: 16,
              textTransform: "none",
              boxShadow: "0 4px 14px rgba(37, 117, 252, 0.4)",
              "&:hover": {
                background: "linear-gradient(135deg, #5b0eaf 0%, #1a5ae0 100%)",
                boxShadow: "0 6px 16px rgba(37, 117, 252, 0.5)",
                transform: "translateY(-2px)",
              },
            }}
            disabled={
              loading ||
              !formData.fullName ||
              !formData.email ||
              !formData.password ||
              formData.password !== formData.confirmPassword
            }
          >
            {loading ? (
              <CircularProgress size={24} sx={{ color: "white" }} />
            ) : (
              "Register"
            )}
          </Button>

          <Typography
            className="register-login-text"
            align="center"
            sx={{ mt: 2 }}
          >
            Already have an account?{" "}
            <Button
              variant="text"
              onClick={() => navigate("/login")}
              className="register-login-button"
            >
              Login
            </Button>
          </Typography>
        </form>
      </Box>

      {/* Snackbar for Success/Error messages */}
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

export default RegisterScreen;
