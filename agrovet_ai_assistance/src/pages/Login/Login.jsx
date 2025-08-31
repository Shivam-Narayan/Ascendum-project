import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, Eye, EyeOff, AlertCircle } from 'lucide-react';
import './Login.css'; 
import { loginUser } from '../../services/LoginApi';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await loginUser({ email, password });
      if (response?.success) {
        navigate('/dashboard');
      } else {
        setError(response?.message || 'Invalid email or password');
      }
    } catch (err) {
      setError('An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        {/* Header */}
        <div className="header">
          <div className="header-content">
            <Leaf className="leaf-icon" />
            <h1 className="main-title">
              AI Assistant for Plant and Soil
            </h1>
          </div>
        </div>

        {/* Login Form */}
        <div className="form-container">
          <h2 className="form-title">Login to Your Account</h2>

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
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
            </div>

            <button
              type="submit"
              disabled={loading}
              className="submit-button"
            >
              {loading ? 'Signing in...' : 'Login'}
            </button>
          </form>

          {/* Register Link */}
          <div className="register-link">
            <p className="register-text">
              Don't have an account?{' '}
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

// import React, { useState } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { useAuth } from '../../contexts/AuthContext';
// import { Leaf, Eye, EyeOff, AlertCircle } from 'lucide-react';
// import './Login.css'; 
// import { loginUser } from '../../services/LoginApi';

// const Login = () => {
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [showPassword, setShowPassword] = useState(false);
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);
//   const { loginUser: authLogin } = useAuth();
//   const navigate = useNavigate();

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError('');
//     setLoading(true);

//     try {
//       const success = await authLogin(email, password);
//       if (success) {
//         navigate('/dashboard');
//       } else {
//         setError('Invalid email or password');
//       }
//     } catch (err) {
//       setError('An error occurred during login');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="login-container">
//       <div className="login-wrapper">
//         {/* Header */}
//         <div className="header">
//           <div className="header-content">
//             <Leaf className="leaf-icon" />
//             <h1 className="main-title">
//               AI Assistant for Plant and Soil
//             </h1>
//           </div>
//         </div>

//         {/* Login Form */}
//         <div className="form-container">
//           <h2 className="form-title">Login</h2>

//           {error && (
//             <div className="error-message">
//               <AlertCircle size={18} />
//               <span className="error-text">{error}</span>
//             </div>
//           )}

//           <form onSubmit={handleSubmit} className="form">
//             <div className="form-group">
//               <label htmlFor="email" className="form-label">
//                 Email Address
//               </label>
//               <input
//                 id="email"
//                 type="email"
//                 required
//                 value={email}
//                 onChange={(e) => setEmail(e.target.value)}
//                 className="form-input"
//                 placeholder="Enter your email"
//               />
//             </div>

//             <div className="form-group">
//               <label htmlFor="password" className="form-label">
//                 Password
//               </label>
//               <div className="password-container">
//                 <input
//                   id="password"
//                   type={showPassword ? 'text' : 'password'}
//                   required
//                   value={password}
//                   onChange={(e) => setPassword(e.target.value)}
//                   className="password-input"
//                   placeholder="Enter your password"
//                 />
//                 <button
//                   type="button"
//                   onClick={() => setShowPassword(!showPassword)}
//                   className="password-toggle"
//                 >
//                   {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
//                 </button>
//               </div>
//             </div>

//             <button
//               type="submit"
//               disabled={loading}
//               className="submit-button"
//             >
//               {loading ? 'Signing in...' : 'Login'}
//             </button>
//           </form>

//           {/* Register Link */}
//           <div className="register-link">
//             <p className="register-text">
//               Don't have an account?{' '}
//               <Link to="/register" className="register-link-text">
//                 Register here
//               </Link>
//             </p>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Login;