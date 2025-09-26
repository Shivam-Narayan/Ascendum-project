import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import "./Dashboard.css";
import AnalyticsDashboard from "./AnalyticsDashboard/AnalyticsDashboard";
import DetectionDashboard from "./DetectionDashboard/DetectionDashboard";
import TrainingModelDashboard from "./TrainingModelDashboard/TrainingModelDashboard";
import LiveDetection from "./LiveDetection/LiveDetection";
import {
  Box,
  Button,
  Typography,
  List,
  ListItemButton,
  ListItemText,
  Divider,
} from "@mui/material";

const theme = createTheme({
  palette: {
    primary: { main: "#00897b" },
    error: { main: "#d32f2f" },
    background: {
      default: "#f1f3f6",
      paper: "#ffffff",
    },
  },
  typography: {
    fontFamily: "'San Francisco', 'Roboto', 'Helvetica Neue', sans-serif",
    h5: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: "4px 8px",
          "&.Mui-selected": {
            backgroundColor: "#b2dfdb",
            color: "#004d40",
          },
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: "4px 8px",
          "&.Mui-selected": {
            backgroundColor: "#e8f0fe",
            color: "#007aff",
          },
        },
      },
    },
  },
});

const Dashboard = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);

  const [selectedSection, setSelectedSection] = useState(() => {
    return localStorage.getItem("selectedSection") || "analytics";
  });

  useEffect(() => {
    localStorage.setItem("selectedSection", selectedSection);
  }, [selectedSection]);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUserData(JSON.parse(storedUser));
    } else {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.clear();
    setUserData(null);
    window.location.href = "/login";
  };

  const renderSection = () => {
    switch (selectedSection) {
      case "analytics":
        return <AnalyticsDashboard />;
      case "training":
        return <TrainingModelDashboard />;
      case "detection":
        return <DetectionDashboard />;
      case "live-detection":
        return <LiveDetection token={localStorage.getItem("token")} />;
      default:
        return null;
    }
  };

  if (!userData) {
    return null;
  }

  return (
    <ThemeProvider theme={theme}>
      <Box className="dashboard-root">
        {/* Sidebar */}
        <Box className="sidebar">
          <Box className="sidebar-title">
            <img src="/logo.ico" alt="Company Logo" className="sidebar-logo" />
            <Typography variant="h5">Seam Guard</Typography>
          </Box>

          <Divider className="sidebar-divider" />

          <List>
            <ListItemButton
              selected={selectedSection === "analytics"}
              onClick={() => setSelectedSection("analytics")}
            >
              <ListItemText primary="Analytics" />
            </ListItemButton>
            <ListItemButton
              selected={selectedSection === "training"}
              onClick={() => setSelectedSection("training")}
            >
              <ListItemText primary="Training Model" />
            </ListItemButton>
            <ListItemButton
              selected={selectedSection === "detection"}
              onClick={() => setSelectedSection("detection")}
            >
              <ListItemText primary="Detection" />
            </ListItemButton>
            <ListItemButton
              selected={selectedSection === "live-detection"}
              onClick={() => setSelectedSection("live-detection")}
            >
              <ListItemText primary="Live Detection" />
            </ListItemButton>
          </List>

          <Box className="sidebar-footer">
            <Button
              variant="contained"
              color="error"
              onClick={handleLogout}
              fullWidth
            >
              Logout
            </Button>
          </Box>
        </Box>

        {/* Main Content */}
        <Box className="dashboard-content">
          <Box
            sx={{
              backgroundColor: "#000",
              color: "#fff",
              borderRadius: "8px",
              padding: "8px 12px",
              display: "inline-block",
            }}
          >
            <Typography variant="subtitle1" sx={{ mb: 0, lineHeight: 1.4 }}>
              Hello <span className="color-id">{userData.name}</span>, you have
              logged into line number{" "}
              <span className="color-line">{userData.line_number}</span> in{" "}
              <span className="color-dept">{userData.department}</span>{" "}
              department of{" "}
              <span className="color-industry">{userData.industry}</span>{" "}
              industry.
            </Typography>
          </Box>
          <Box className="dashboard-inner-content">{renderSection()}</Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default Dashboard;
