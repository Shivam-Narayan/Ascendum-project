import { Routes, Route, Navigate } from "react-router-dom";
import type React from "react";
import SplashScreen from "./pages/SplashScreen/SplashScreen";
import LoginScreen from "./pages/LoginScreen/LoginScreen";
import RegisterScreen from "./pages/RegisterScreen/RegisterScreen";
import HomeScreen from "./pages/HomeScreen/HomeScreen";

// Inline wrapper for protected routes
const PrivateRoute = ({ children }: { children: React.ReactElement }) => {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <Routes>
      <Route path="/" element={<SplashScreen />} />
      <Route path="/login" element={<LoginScreen />} />
      <Route path="/register" element={<RegisterScreen />} />

      {/* Protected route */}
      <Route
        path="/home"
        element={
          <PrivateRoute>
            <HomeScreen />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

export default App;
