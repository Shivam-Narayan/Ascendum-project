import React, { useState, useEffect } from "react";
import loginuser from "../../services/LoginApi";
import "./LoginScreen.css";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isFocused, setIsFocused] = useState({
    email: false,
    password: false
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
    
    // Check if user is already logged in (has token)
    const token = localStorage.getItem('token');
    if (token) {
      navigate('/home');
    }
  }, [isDarkMode, navigate]);

  const handleFocus = (field) => {
    setIsFocused(prev => ({ ...prev, [field]: true }));
    setError(""); 
  };

  const handleBlur = (field) => {
    setIsFocused(prev => ({ ...prev, [field]: false }));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    
    if (!email || !password) {
      setError("Please enter both email and password");
      return;
    }
  
    setIsLoading(true);
    
    try {
      const response = await loginuser(email, password);
      console.log("Login response:", response);
      
      if (response.token) {
        // Store token in localStorage
        localStorage.setItem('token', response.token);
        localStorage.setItem('userEmail', email);

        const userThemeKey = `userTheme_${email}`;
        if (!localStorage.getItem(userThemeKey)) {
          localStorage.setItem(userThemeKey, JSON.stringify(false)); // Default to light theme
        }

        setSuccess("Login successful! Redirecting...");
        
        // Redirect after 0.5 seconds
        setTimeout(() => {
          navigate('/home');
        }, 500);
      } else {
        setError(response.message || "Login failed - no token received");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError(err.message || "Invalid username or password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <button 
        className="login-theme-toggle"
        onClick={() => setIsDarkMode(!isDarkMode)}
      >
        {isDarkMode ? '☀️' : '🌙'}
      </button>
      <h1 className="login-title">Welcome Back</h1>
      <form onSubmit={handleLogin} className="login-form">
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        {success && (
          <div className="success-message">
            {success}
          </div>
        )}
        
        <div className={`input-group ${isFocused.email || email ? "focused" : ""}`}>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onFocus={() => handleFocus("email")}
            onBlur={() => handleBlur("email")}
            required
          />
          <label htmlFor="email" className={isFocused.email || email ? "shrink" : ""}>
            Email
          </label>
        </div>
        
        <div className={`input-group ${isFocused.password || password ? "focused" : ""}`}>
          <input
            type={showPassword ? "text" : "password"}
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onFocus={() => handleFocus("password")}
            onBlur={() => handleBlur("password")}
            required
          />
          <label htmlFor="password" className={isFocused.password || password ? "shrink" : ""}>
            Password
          </label>
          <button
            type="button"
            className="toggle-password"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5C5 5 1 12 1 12C1 12 5 19 12 19C19 19 23 12 23 12C23 12 19 5 12 5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M1 12C1 12 5 20 12 20C19 20 23 12 23 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M2 2L22 22" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            )}
          </button>
        </div>
        
        <button 
          type="submit" 
          className="login-button"
          disabled={isLoading || !email || !password}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Signing In...
            </>
          ) : "Sign In"}
        </button>
      </form>
    </div>
  );
};

export default Login;