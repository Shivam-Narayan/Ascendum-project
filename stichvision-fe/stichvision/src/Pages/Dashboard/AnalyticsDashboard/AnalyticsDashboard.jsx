import React, { useState, useEffect, useMemo } from "react";
import "./AnalyticsDashboard.css";
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  CircularProgress,
  useTheme,
} from "@mui/material";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  Cell,
} from "recharts";
import { format, parseISO } from "date-fns";
import {
  fetchDefectsByDate,
  fetchLoginDetails,
  fetchTotalAnnotatedImages,
} from "../../../Services/AnalyticsModuleApi";

const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884D8",
  "#82CA9D",
];

const parseDefectResults = (defectResult) => {
  try {
    return JSON.parse(defectResult);
  } catch (e) {
    console.error("Error parsing defect result:", e);
    return [];
  }
};

// Enhanced Custom Tooltip Component
const CustomTooltip = ({ active, payload, label, chartType }) => {
  if (active && payload && payload.length) {
    const dataItem = payload[0].payload;

    return (
      <div
        className="custom-tooltip"
        style={{
          background: "#fff",
          padding: "12px",
          borderRadius: "8px",
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.15)",
          border: "none",
          minWidth: "200px",
        }}
      >
        <p style={{ fontWeight: 600, marginBottom: "8px", color: "#333" }}>
          {label}
        </p>

        {chartType === "hourly" ? (
          <>
            <p style={{ color: "#555", marginBottom: "8px" }}>
              Total Defects: <strong>{payload[0].value}</strong>
            </p>
            {dataItem.defects && (
              <div>
                <p style={{ fontWeight: 500, marginBottom: "4px" }}>
                  Defect Breakdown:
                </p>
                {Object.entries(dataItem.defects).map(
                  ([defectType, count], index) => (
                    <p
                      key={`defect-${index}`}
                      style={{
                        color: COLORS[index % COLORS.length],
                        marginBottom: "2px",
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>{defectType}:</span>
                      <strong>{count}</strong>
                    </p>
                  )
                )}
              </div>
            )}
          </>
        ) : chartType === "defectTypes" ? (
          <div>
            {payload.map((entry, index) => (
              <p
                key={`tooltip-${index}`}
                style={{ color: entry.color, marginBottom: "4px" }}
              >
                {entry.name}: <strong>{entry.value}</strong>
              </p>
            ))}
          </div>
        ) : null}
      </div>
    );
  }
  return null;
};

const AnalyticsDashboard = () => {
  const theme = useTheme();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [defectsData, setDefectsData] = useState([]);
  const [loginDetails, setLoginDetails] = useState(null);
  const [totalImages, setTotalImages] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Memoized data processing for better performance
  const { defectDistribution, hourlyDefects, defectTypesByHour } =
    useMemo(() => {
      const defectCounts = {};
      const hourlyCounts = {};
      const hourlyDefectDetails = {};
      const typeHourlyCounts = {};

      defectsData.forEach((entry) => {
        entry.detections.forEach((detection) => {
          // Process hourly data
          const hour = detection.time.split(":")[0];
          hourlyCounts[hour] = (hourlyCounts[hour] || 0) + 1;

          // Initialize defect details for this hour if not exists
          if (!hourlyDefectDetails[hour]) {
            hourlyDefectDetails[hour] = {};
          }

          // Process defect types by hour
          if (!typeHourlyCounts[hour]) {
            typeHourlyCounts[hour] = {};
          }

          const defects = parseDefectResults(detection.defect_result);
          defects.forEach((defect) => {
            // Count defect types
            defectCounts[defect.class] = (defectCounts[defect.class] || 0) + 1;

            // Count defect types by hour
            typeHourlyCounts[hour][defect.class] =
              (typeHourlyCounts[hour][defect.class] || 0) + 1;

            // Track defect details by hour
            hourlyDefectDetails[hour][defect.class] =
              (hourlyDefectDetails[hour][defect.class] || 0) + 1;
          });
        });
      });

      // Convert to array formats for charts
      const defectDistribution = Object.entries(defectCounts).map(
        ([name, value]) => ({ name, value })
      );

      const hourlyDefects = Object.entries(hourlyCounts)
        .map(([hour, count]) => ({
          hour: `${hour}:00`,
          count,
          defects: hourlyDefectDetails[hour],
        }))
        .sort((a, b) => a.hour.localeCompare(b.hour));

      const defectTypesByHour = Object.entries(typeHourlyCounts)
        .map(([hour, types]) => {
          const entry = { hour: `${hour}:00` };
          Object.entries(types).forEach(([type, count]) => {
            entry[type] = count;
          });
          return entry;
        })
        .sort((a, b) => a.hour.localeCompare(b.hour));

      return { defectDistribution, hourlyDefects, defectTypesByHour };
    }, [defectsData]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const dateStr = format(selectedDate, "yyyy-MM-dd");

        const [defectsRes, loginRes, imagesRes] = await Promise.all([
          fetchDefectsByDate(dateStr),
          fetchLoginDetails(),
          fetchTotalAnnotatedImages(),
        ]);

        setDefectsData(defectsRes || []);
        setLoginDetails(loginRes);
        setTotalImages(imagesRes);
        setError(null);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError(err.message || "Failed to load data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    // Add debounce to prevent rapid API calls when changing date
    const timer = setTimeout(fetchData, 300);
    return () => clearTimeout(timer);
  }, [selectedDate]);

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="60vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="60vh"
      >
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <div className="analytics-container">
      <Box sx={{ width: "100%", maxWidth: "1800px" }}>
        <CardContent>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={3}
          >
            <Typography
              variant="h4"
              component="h1"
              color="primary"
              sx={{ fontWeight: "bold" }}
            >
              Analytics Dashboard
            </Typography>
            <input
              type="date"
              value={format(selectedDate, "yyyy-MM-dd")}
              onChange={(e) => setSelectedDate(new Date(e.target.value))}
              className="date-picker"
            />
          </Box>

          {loginDetails && (
            <Card
              variant="outlined"
              sx={{
                mb: 3,
                p: 2,
                borderRadius: "16px",
                background: "rgba(255, 255, 255, 0.1)",
                backdropFilter: "blur(10px)",
                WebkitBackdropFilter: "blur(10px)",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                boxShadow: "0 4px 30px rgba(0, 0, 0, 0.1)",
              }}
            >
              <Typography variant="h6" gutterBottom sx={{ fontWeight: "600" }}>
                Line Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body1">
                    <strong>Line Number:</strong> {loginDetails.line_number}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body1">
                    <strong>Department:</strong> {loginDetails.department}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body1">
                    <strong>Account Created:</strong>{" "}
                    {format(parseISO(loginDetails.created_time), "PPpp")}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body1">
                    <strong>Total Annotated Images:</strong>{" "}
                    {totalImages?.total_annotated_images}
                  </Typography>
                </Grid>
              </Grid>
            </Card>
          )}

          <Grid
            container
            spacing={3}
            direction="column"
            sx={{ mb: 3, width: "100%", m: 0 }}
          >
            {/* ---- Bar Chart (Full Width) ---- */}
            <Grid item xs={12} sx={{ width: 1, minWidth: 0 }}>
              <Card
                sx={{
                  height: "100%",
                  width: "100%",
                  display: "flex",
                  flexDirection: "column",
                  borderRadius: "16px",
                  boxShadow: 4,
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontWeight: "600" }}
                  >
                    Defects by Hour
                  </Typography>
                  <Box sx={{ height: 350, mt: 2, width: 1, minWidth: 0 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={hourlyDefects}
                        margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                        <XAxis
                          dataKey="hour"
                          tick={{ fill: theme.palette.text.secondary }}
                        />
                        <YAxis tick={{ fill: theme.palette.text.secondary }} />
                        <Tooltip
                          content={<CustomTooltip chartType="hourly" />}
                        />
                        <Legend />
                        <Bar dataKey="count" name="Defects">
                          {hourlyDefects.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={COLORS[index % COLORS.length]}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* ---- Line Chart (Full Width) ---- */}
            <Grid item xs={12} sx={{ width: 1, minWidth: 0 }}>
              <Card
                sx={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  borderRadius: "16px",
                  boxShadow: 4,
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontWeight: "600" }}
                  >
                    Defect Trends by Hour
                  </Typography>
                  <Box sx={{ height: 350, mt: 2, width: 1, minWidth: 0 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={hourlyDefects}
                        margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                        <XAxis
                          dataKey="hour"
                          tick={{ fill: theme.palette.text.secondary }}
                        />
                        <YAxis tick={{ fill: theme.palette.text.secondary }} />
                        <Tooltip
                          content={<CustomTooltip chartType="hourly" />}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="count"
                          stroke="#8884d8"
                          strokeWidth={2}
                          dot={{ r: 4 }}
                          activeDot={{
                            r: 6,
                            stroke: "#8884d8",
                            strokeWidth: 2,
                          }}
                          name="Defects"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* ---- Stacked Bar Chart (Full Width) ---- */}
            {defectTypesByHour.length > 0 && (
              <Grid item xs={12} sx={{ width: 1, minWidth: 0 }}>
                <Card
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    borderRadius: "16px",
                    boxShadow: 4,
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography
                      variant="h6"
                      gutterBottom
                      sx={{ fontWeight: "600" }}
                    >
                      Defect Types by Hour
                    </Typography>
                    <Box sx={{ height: 400, mt: 2, width: 1, minWidth: 0 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={defectTypesByHour}
                          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                          stackOffset="expand"
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                          <XAxis
                            dataKey="hour"
                            tick={{ fill: theme.palette.text.secondary }}
                          />
                          <YAxis
                            tick={{ fill: theme.palette.text.secondary }}
                          />
                          <Tooltip
                            content={<CustomTooltip chartType="defectTypes" />}
                          />
                          <Legend />
                          {defectDistribution.map((defect, index) => (
                            <Bar
                              key={defect.name}
                              dataKey={defect.name}
                              stackId="a"
                              fill={COLORS[index % COLORS.length]}
                              name={defect.name}
                            />
                          ))}
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>

          <Card
            sx={{ mt: 3, borderRadius: "16px", boxShadow: 4, width: "100%" }}
          >
            <CardContent>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ fontWeight: "600", textAlign: "center" }}
              >
                Detailed Defect Statistics - {format(selectedDate, "PPPP")}
              </Typography>

              {defectDistribution.length > 0 ? (
                <Grid
                  container
                  spacing={3}
                  direction="column"
                  sx={{ width: "100%", m: 0 }}
                >
                  {/* ---- Bar Chart (Full Width, stacked) ---- */}
                  <Grid item xs={12} sx={{ width: 1, minWidth: 0 }}>
                    <Typography
                      variant="subtitle1"
                      gutterBottom
                      sx={{ fontWeight: "500" }}
                    >
                      Defect Distribution
                    </Typography>

                    <Box
                      sx={{
                        width: 1,
                        minWidth: 0,
                        height: { xs: 320, sm: 360, md: 400 },
                        mt: 2,
                      }}
                    >
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={defectDistribution}
                          layout="vertical"
                          margin={{ top: 5, right: 24, left: 8, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                          <XAxis
                            type="number"
                            tick={{ fill: theme.palette.text.secondary }}
                          />
                          <YAxis
                            dataKey="name"
                            type="category"
                            width={140}
                            tick={{ fill: theme.palette.text.secondary }}
                          />
                          <Tooltip
                            content={<CustomTooltip chartType="defectTypes" />}
                          />
                          <Legend />
                          <Bar dataKey="value" name="Count">
                            {defectDistribution.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </Grid>

                  {/* ---- Line Chart (Full Width, stacked) ---- */}
                  <Grid item xs={12} sx={{ width: 1, minWidth: 0 }}>
                    <Typography
                      variant="subtitle1"
                      gutterBottom
                      sx={{ fontWeight: "500" }}
                    >
                      Defect Types Over Time
                    </Typography>

                    <Box
                      sx={{
                        width: 1,
                        minWidth: 0,
                        height: { xs: 320, sm: 360, md: 400 },
                        mt: 2,
                      }}
                    >
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                          data={defectTypesByHour}
                          margin={{ top: 5, right: 24, left: 8, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                          <XAxis
                            dataKey="hour"
                            tick={{ fill: theme.palette.text.secondary }}
                          />
                          <YAxis
                            tick={{ fill: theme.palette.text.secondary }}
                          />
                          <Tooltip
                            content={<CustomTooltip chartType="defectTypes" />}
                          />
                          <Legend />
                          {defectDistribution
                            .slice(0, 4)
                            .map((defect, index) => (
                              <Line
                                key={defect.name}
                                type="monotone"
                                dataKey={defect.name}
                                stroke={COLORS[index % COLORS.length]}
                                strokeWidth={2}
                                dot={{ r: 3 }}
                                activeDot={{
                                  r: 5,
                                  stroke: COLORS[index % COLORS.length],
                                  strokeWidth: 2,
                                }}
                                name={defect.name}
                              />
                            ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </Box>
                  </Grid>
                </Grid>
              ) : (
                <Typography variant="body1" color="text.secondary">
                  No defects recorded for this date.
                </Typography>
              )}
            </CardContent>
          </Card>
        </CardContent>
      </Box>
    </div>
  );
};

export default AnalyticsDashboard;
