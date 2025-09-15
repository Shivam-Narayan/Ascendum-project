import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Leaf, Eye, EyeOff, AlertCircle } from "lucide-react";
import "./Login.css";
import { loginUser } from "../../services/LoginApi";

const Login = () => {
  // Using a hash map (object) for form fields -> O(1) access
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false); // toggle (two-pointer like idea)
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Check if form is valid for submission
  const isFormValid = formData.email.trim() !== "" && formData.password.trim() !== "";

  // Efficient form handler using keys (instead of separate states)
  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id]: value, // O(1) update
    }));
  };

  // Validation using greedy strategy: fail fast if invalid
  const validateForm = () => {
    if (!formData.email.includes("@")) {
      setError("Invalid email format");
      return false;
    }
    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return false;
    }
    return true;
  };

  // Queue-like async request handling
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!validateForm()) return; // early exit

    setLoading(true);

    try {
      const response = await loginUser(formData);

      // Store token and user data in localStorage (if available in response)
      if (response.token) {
        localStorage.setItem("token", response.token);
      }
      if (response.user) {
        localStorage.setItem("user", JSON.stringify(response.user));
      }

      // Redirect to dashboard immediately
      navigate("/dashboard");

    } catch (err) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false); // dequeue
    }
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        {/* Header */}
        <div className="header">
          <div className="header-content">
            <Leaf className="leaf-icon" />
            <h2 className="main-title">AI Assistant for Plant and Soil</h2>
          </div>
        </div>

        {/* Login Form */}
        <div className="form-container">
          <h1 className="form-title">Login </h1>

          {error && (
            <div className="error-message">
              <AlertCircle size={18} />
              <span className="error-text">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter your email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className="password-container">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="password-input"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)} // toggle like two-pointer swap
                  className="password-toggle"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading || !isFormValid} 
              className="submit-button"
            >
              {loading ? "Signing in..." : "Login"}
            </button>
          </form>

          {/* Register Link */}
          <div className="register-link">
            <p className="register-text">
              Don&apos;t have an account?{" "}
              <Link to="/register" className="register-link-text">
                Register here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;