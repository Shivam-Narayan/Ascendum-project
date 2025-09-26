import React, { useState } from "react";
import { Logout } from "@mui/icons-material";
import "./AdminDashboard.css";
import UserManagement from "./UserManagement/UserManagement";
import AdminReports from "./AdminReports/AdminReports";
import AdminAnalytics from "./AdminAnalytics/AdminAnalytics";
import AdminTrainModel from "./AdminTrainModel/AdminTrainModel";

function AdminDashboard() {
  const adminUser = JSON.parse(localStorage.getItem("adminUser"));

  const [activeTab, setActiveTab] = useState("user");

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/login";
  };

  const renderContent = () => {
    switch (activeTab) {
      case "user":
        return <UserManagement />;
      case "reports":
        return <AdminReports />;
      case "analytics":
        return <AdminAnalytics />;
      case "train":
        return <AdminTrainModel />;
      default:
        return <UserManagement />;
    }
  };

  return (
    <div className="adminDashboard-container">
      <header className="adminDashboard-header">
        <div className="adminDashboard-welcomeBox">
          <p>
            Hi{" "}
            <span className="adminDashboard-highlightUsername">
              {adminUser?.emp_id || "ADMIN123"}
            </span>
            , you have logged into{" "}
            <span className="adminDashboard-highlightPortal">Admin Portal</span>
          </p>
        </div>

        <button className="adminDashboard-logoutBtn" onClick={handleLogout}>
          <Logout />
        </button>
      </header>

      <main className="adminDashboard-main">
        <div
          className="adminDashboard-card adminDashboard-userManagement"
          onClick={() => setActiveTab("user")}
        >
          <h2>User Management</h2>
        </div>
        <div
          className="adminDashboard-card adminDashboard-reports"
          onClick={() => setActiveTab("reports")}
        >
          <h2>Reports</h2>
        </div>
        <div
          className="adminDashboard-card adminDashboard-analytics"
          onClick={() => setActiveTab("analytics")}
        >
          <h2>Analytics</h2>
        </div>
        <div
          className="adminDashboard-card adminDashboard-trainModel"
          onClick={() => setActiveTab("train")}
        >
          <h2>Train Model</h2>
        </div>
      </main>

      {renderContent()}
    </div>
  );
}

export default AdminDashboard;
