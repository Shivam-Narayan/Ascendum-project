import React, { useState, useEffect } from "react";
import "./AdminAnalytics.css";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ComposedChart,
  Scatter
} from "recharts";
import { fetchAdminAnalytics } from "../../../Services/UserManagementApi";

function AdminAnalytics() {
  const [analyticsData, setAnalyticsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const token = localStorage.getItem("adminToken");

  useEffect(() => {
    const getAnalytics = async () => {
      try {
        const data = await fetchAdminAnalytics(token);
        setAnalyticsData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    getAnalytics();
  }, [token]);

  // Prepare chart data
  const detectionsData = analyticsData.map((user) => ({
    name: user.EMP_ID,
    detections_today: user.detections_today,
  }));

  const annotationsData = analyticsData.map((user) => ({
    name: user.EMP_ID,
    annotations_total: user.annotations_total,
  }));

  const loginsData = analyticsData.map((user) => ({
    name: user.EMP_ID,
    logins_total: user.logins_total,
  }));

  // For Pie Chart (Defect Types)
  const defectTypesData = [];
  analyticsData.forEach((user) => {
    Object.entries(user.defect_types_today).forEach(([key, value]) => {
      const existing = defectTypesData.find((item) => item.name === key);
      if (existing) {
        existing.value += value;
      } else {
        defectTypesData.push({ name: key, value });
      }
    });
  });

  // Activity timeline data (simulated)
  const activityTimelineData = [
    { time: "9:00", activity: 40 },
    { time: "10:00", activity: 30 },
    { time: "11:00", activity: 60 },
    { time: "12:00", activity: 50 },
    { time: "13:00", activity: 70 },
    { time: "14:00", activity: 90 },
    { time: "15:00", activity: 85 },
    { time: "16:00", activity: 65 },
    { time: "17:00", activity: 45 },
  ];

  // Performance radar data
  const performanceData = analyticsData.map(user => ({
    subject: user.EMP_ID,
    detections: user.detections_today,
    annotations: Math.min(user.annotations_total / 10, 100), // Normalized for radar
    logins: Math.min(user.logins_total / 5, 100), // Normalized for radar
    fullMark: 100,
  }));

  // Summary statistics
  const totalDetections = detectionsData.reduce((sum, item) => sum + item.detections_today, 0);
  const totalAnnotations = annotationsData.reduce((sum, item) => sum + item.annotations_total, 0);
  const totalLogins = loginsData.reduce((sum, item) => sum + item.logins_total, 0);
  const totalDefects = defectTypesData.reduce((sum, item) => sum + item.value, 0);

  const COLORS = ["#0088FE", "#FF8042", "#00C49F", "#FFBB28", "#FF6B6B", "#6A0DAD"];

  if (loading) return (
    <div className="adminAnalytics-container">
      <div className="adminAnalytics-loading-spinner"></div>
      <p>Loading analytics data...</p>
    </div>
  );
  
  if (error) return (
    <div className="adminAnalytics-container">
      <div className="adminAnalytics-error-message">
        <h3>Error Loading Data</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </div>
    </div>
  );

  return (
    <div className="adminAnalytics-container">
      <h2>Admin Analytics Dashboard</h2>
      
      {/* Summary Cards */}
      <div className="adminAnalytics-summary-cards">
        <div className="adminAnalytics-summary-card adminAnalytics-detection-card">
          <div className="adminAnalytics-card-icon"></div>
          <h3>Total Detections</h3>
          <p className="adminAnalytics-stat-number">{totalDetections}</p>
          <span className="adminAnalytics-stat-label">Today</span>
        </div>
        <div className="adminAnalytics-summary-card adminAnalytics-annotation-card">
          <div className="adminAnalytics-card-icon"></div>
          <h3>Total Annotations</h3>
          <p className="adminAnalytics-stat-number">{totalAnnotations}</p>
          <span className="adminAnalytics-stat-label">All Time</span>
        </div>
        <div className="adminAnalytics-summary-card adminAnalytics-login-card">
          <div className="adminAnalytics-card-icon"></div>
          <h3>Total Logins</h3>
          <p className="adminAnalytics-stat-number">{totalLogins}</p>
          <span className="adminAnalytics-stat-label">All Time</span>
        </div>
        <div className="adminAnalytics-summary-card adminAnalytics-defect-card">
          <div className="adminAnalytics-card-icon"></div>
          <h3>Defects Identified</h3>
          <p className="adminAnalytics-stat-number">{totalDefects}</p>
          <span className="adminAnalytics-stat-label">Today</span>
        </div>
      </div>
      
      {/* Tab Navigation */}
      <div className="adminAnalytics-tab-navigation">
        <button 
          className={activeTab === "overview" ? "adminAnalytics-tab-btn adminAnalytics-active" : "adminAnalytics-tab-btn"} 
          onClick={() => setActiveTab("overview")}
        >
          Overview
        </button>
        <button 
          className={activeTab === "details" ? "adminAnalytics-tab-btn adminAnalytics-active" : "adminAnalytics-tab-btn"} 
          onClick={() => setActiveTab("details")}
        >
          Detailed View
        </button>
      </div>

      {/* Charts Container */}
      <div className="adminAnalytics-charts-container">
        {activeTab === "overview" ? (
          <div className="adminAnalytics-charts-grid">
            {/* Detections Area Chart */}
            <div className="adminAnalytics-chart-card">
              <h3>Detections Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={detectionsData}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="detections_today" fill="#8884d8" stroke="#8884d8" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Defect Types Pie Chart */}
            <div className="adminAnalytics-chart-card">
              <h3>Defect Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={defectTypesData}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={120}
                    label
                  >
                    {defectTypesData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Annotations Line Chart */}
            <div className="adminAnalytics-chart-card">
              <h3>Annotations Progress</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={annotationsData}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="annotations_total" stroke="#82ca9d" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Performance Radar Chart */}
            <div className="adminAnalytics-chart-card">
              <h3>Employee Performance</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={performanceData[0] ? performanceData : [{subject: 'No Data', detections: 0, annotations: 0, logins: 0}]}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" />
                  <PolarRadiusAxis />
                  <Radar name="Performance" dataKey="detections" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Activity Timeline */}
            <div className="adminAnalytics-chart-card">
              <h3>Daily Activity Pattern</h3>
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={activityTimelineData}>
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="activity" fill="#ffc658" stroke="#ffc658" />
                  <Line type="monotone" dataKey="activity" stroke="#ff7300" />
                  <Scatter dataKey="activity" fill="red" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* Logins Bar Chart with different style */}
            <div className="adminAnalytics-chart-card">
              <h3>Login Frequency</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={loginsData}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="logins_total" fill="#413ea0" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : (
          <div className="adminAnalytics-detailed-view">
            <div className="adminAnalytics-data-table">
              <h3>Employee Analytics Details</h3>
              <table>
                <thead>
                  <tr>
                    <th>Employee ID</th>
                    <th>Detections Today</th>
                    <th>Annotations Total</th>
                    <th>Logins Total</th>
                    <th>Defects Today</th>
                  </tr>
                </thead>
                <tbody>
                  {analyticsData.map((user, index) => (
                    <tr key={index}>
                      <td>{user.EMP_ID}</td>
                      <td>{user.detections_today}</td>
                      <td>{user.annotations_total}</td>
                      <td>{user.logins_total}</td>
                      <td>{Object.values(user.defect_types_today).reduce((a, b) => a + b, 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminAnalytics;