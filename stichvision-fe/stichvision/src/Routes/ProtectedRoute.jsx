import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, admin = false }) => {
  if (admin) {
    // For admin routes, check adminToken
    const adminToken = localStorage.getItem('adminToken');
    if (!adminToken) {
      return <Navigate to="/admin/login" replace />;
    }
  } else {
    // For regular user routes, check user token
    const user = localStorage.getItem('user');
    if (!user) {
      return <Navigate to="/login" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;