import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import Dashboard from './pages/Dashboard/Dashboard';
import SoilNutrition from './pages/SoilNutrition/SoilNutrition';
import PlantDisease from './pages/PlantDisease/PlantDisease';
import CottonPests from './pages/CottonPests/CottonPests';
import TomatoRipeness from './pages/TomatoRipeness/TomatoRipeness';
import BananaRipeness from './pages/BananaRipeness/BananaRipeness';
import MangoRipeness from './pages/MangoRipeness/MangoRipeness';

// Private Route component to protect authenticated routes
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  return token ? children : React.createElement(Navigate, { to: '/login', replace: true });
};

function App() {
  return React.createElement(
    AuthProvider,
    null,
    React.createElement(
      Router,
      null,
      React.createElement(
        'div',
        { className: 'min-h-screen bg-gradient-to-br from-green-50 via-white to-amber-50' },
        React.createElement(
          Routes,
          null,
          // Public routes (no authentication required)
          React.createElement(Route, { path: '/login', element: React.createElement(Login, null) }),
          React.createElement(Route, { path: '/register', element: React.createElement(Register, null) }),
          
          // Protected routes (authentication required)
          React.createElement(Route, {
            path: '/dashboard',
            element: React.createElement(
              PrivateRoute,
              null,
              React.createElement(Dashboard, null)
            )
          }),
          React.createElement(Route, {
            path: '/soil-nutrition',
            element: React.createElement(
              PrivateRoute,
              null,
              React.createElement(SoilNutrition, null)
            )
          }),
          React.createElement(Route, {
            path: '/plant-disease',
            element: React.createElement(
              PrivateRoute,
              null,
              React.createElement(PlantDisease, null)
            )
          }),
          React.createElement(Route, {
            path: '/cotton-pests',
            element: React.createElement(
              PrivateRoute,
              null,
              React.createElement(CottonPests, null)
            )
          }),
          React.createElement(Route, {
            path: '/tomato-ripeness',
            element: React.createElement(
              PrivateRoute,
              null,
              React.createElement(TomatoRipeness, null)
            )
          }),
          React.createElement(Route, {
            path: '/banana-ripeness',
            element: React.createElement(
              PrivateRoute,
              null,
              React.createElement(BananaRipeness, null)
            )
          }),
          React.createElement(Route, {
            path: '/mango-ripeness',
            element: React.createElement(
              PrivateRoute,
              null,
              React.createElement(MangoRipeness, null)
            )
          }),
          
          // Root route - redirect based on authentication
          React.createElement(Route, {
            path: '/',
            element: React.createElement(Navigate, { 
              to: localStorage.getItem("token") ? '/dashboard' : '/login', 
              replace: true 
            })
          })
        )
      )
    )
  );
}

export default App;
