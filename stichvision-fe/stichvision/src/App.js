import './App.css';
import SplashScreen from './Pages/SplashScreen';
import LoginScreen from './Pages/LoginScreen/loginscreen';
import RegisterScreen from './Pages/RegisterScreen/registerscreen';
import AdminLoginScreen from './Pages/LoginScreen/AdminLoginScreen';
import Dashboard from './Pages/Dashboard';
import ProtectedRoute from './Routes/ProtectedRoute';
import AdminDashboard from './Pages/AdminDashboard/AdminDashboard';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<SplashScreen />} />
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/register" element={<RegisterScreen />} />
          <Route path="/admin/login" element={<AdminLoginScreen />} />
          
          {/* Protected Route for regular users */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          
          {/* Protected Route for admin with admin prop */}
          <Route
            path="/admin/AdminDashboard"
            element={
              <ProtectedRoute admin={true}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          /> 
        </Routes>
      </Router>
    </div>
  );
}

export default App;