import React, { useState } from "react";
import "./AdminReports.css";
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
  LabelList,
} from "recharts";
import { fetchUserReports } from "../../../Services/UserManagementApi";

function AdminReports() {
  const [employeeId, setEmployeeId] = useState("");
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);
      setReportData(null);

      const token = localStorage.getItem("adminToken");
      const data = await fetchUserReports(employeeId, token);
      setReportData(data);
    } catch (err) {
      setError(err.message);
      setReportData(null);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  // Data prep
  const barData = reportData
    ? [
        { name: "Annotations", value: reportData.annotations_total },
        { name: "Detections Today", value: reportData.detections_today },
        { name: "Logins", value: reportData.logins_total },
      ]
    : [];

  const pieData = reportData
    ? Object.entries(reportData.defect_types_today).map(([key, value]) => ({
        name: key,
        value,
      }))
    : [];

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="adminReportsCustomTooltip">
          <p>
            <strong>{label}</strong>
          </p>
          <p>Value: {payload[0].value}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="adminReportsContainer">
      <h2>Admin Reports</h2>

      {/* Employee Search */}
      <div className="adminReportsEmployeeInput">
        <input
          type="text"
          placeholder="Enter Employee ID (e.g. EMP004)"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          className="adminReportsEmployeeIdInput"
        />
        <button 
          onClick={fetchReports} 
          disabled={!employeeId.trim()}
          className="adminReportsFetchButton"
        >
          Fetch Reports
        </button>
      </div>

      {/* Loading & Error */}
      {loading && <div className="adminReportsLoading">⏳ Loading Reports...</div>}
      {error && <div className="adminReportsErrorBox">{error}</div>}

      {/* Reports */}
      {reportData && (
        <div className="adminReportsChartsGrid">
          {/* Bar Chart */}
          <div className="adminReportsChartCard">
            <h3>Overall Stats</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={barData}
                margin={{ top: 30, right: 20, left: 20, bottom: 20 }}
              >
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar dataKey="value" fill="#1976d2" radius={[6, 6, 0, 0]}>
                  <LabelList
                    dataKey="value"
                    position="top"
                    offset={8}
                    style={{ fill: "#000", fontWeight: "bold"}}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Pie Chart */}
          <div className="adminReportsChartCard">
            <h3>Defect Types Today</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart margin={{ top: 30, right: 30, left: 30, bottom: 1 }}>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={100}
                  label={({ name, value, percent }) =>
                    `${name}: ${value} (${(percent * 100).toFixed(1)}%)`
                  }
                  labelLine={true}
                >
                  {pieData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value}`, `${name}`]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminReports;
