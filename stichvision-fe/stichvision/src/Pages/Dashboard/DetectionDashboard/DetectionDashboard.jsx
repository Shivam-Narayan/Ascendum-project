import React, { useState, useEffect } from "react";
import "./DetectionDashboard.css";
import {
  CardContent,
  Typography,
  MenuItem,
  FormControl,
  Select,
  Box,
  Paper,
  Button,
  CircularProgress,
  IconButton,
  Chip,
} from "@mui/material";
import {
  uploadImagesForDetection,
  getDefectDetails,
  uploadVideoForDetection,
  getVideoDefectDetails,
} from "../../../Services/DetectionModuleApi";
import DeleteIcon from "@mui/icons-material/Delete";
import { set, get, del } from "idb-keyval";

const DetectionDashboard = () => {
  const [selectedOption, setSelectedOption] = useState("image");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [imagePairs, setImagePairs] = useState([]);
  const [videoResults, setVideoResults] = useState(null);

  // Helper function to get color based on defect class
  const getClassColor = (className) => {
    switch (className.toLowerCase()) {
      case "broken stitch":
        return "#d32f2f";
      case "skipped stitch":
        return "#ffa000";
      case "overlapped stitch":
        return "#7b1fa2";
      case "normal stitch":
        return "#388e3c";
      default:
        return "#1976d2";
    }
  };

  // Load metadata from localStorage and blobs from IndexedDB
  useEffect(() => {
    const loadSavedData = async () => {
      // Load images
      const savedImageMeta = localStorage.getItem("detectionImagePairs");
      if (savedImageMeta) {
        try {
          const parsed = JSON.parse(savedImageMeta);
          const loadedImagePairs = await Promise.all(
            parsed.map(async (meta) => {
              const originalData = await get(meta.originalKey);
              const resultData = meta.resultKey ? await get(meta.resultKey) : null;

              const safeBlob = async (data) => {
                if (!data) return null;
                if (data instanceof Blob) return data;
                                if (data instanceof ArrayBuffer) return new Blob([data]);
                if (typeof data === "string" && data.startsWith("data:")) {
                  const res = await fetch(data);
                  return await res.blob();
                }
                return null;
              };

              const originalBlob = await safeBlob(originalData);
              const resultBlob = await safeBlob(resultData);

              return {
                ...meta,
                original: originalBlob ? URL.createObjectURL(originalBlob) : null,
                result: resultBlob ? URL.createObjectURL(resultBlob) : null,
                loading: false,
              };
            })
          );
          setImagePairs(loadedImagePairs);
        } catch (e) {
          console.error("Failed to parse saved image metadata", e);
        }
      }

      // Load video
      const savedVideoMeta = localStorage.getItem("detectionVideoResults");
      if (savedVideoMeta) {
        try {
          const parsed = JSON.parse(savedVideoMeta);
          setVideoResults(parsed);
        } catch (e) {
          console.error("Failed to parse saved video metadata", e);
        }
      }
    };

    loadSavedData();
  }, []);

  const saveImageMetadata = (pairs) => {
    const metadata = pairs.map(
      ({ id, fileName, originalKey, resultKey, classes }) => ({
        id,
        fileName,
        originalKey,
        resultKey,
        classes,
      })
    );
    localStorage.setItem("detectionImagePairs", JSON.stringify(metadata));
  };

  const saveVideoMetadata = (results) => {
    localStorage.setItem("detectionVideoResults", JSON.stringify(results));
  };

  const handleChange = (event) => {
    const newOption = event.target.value;
    setSelectedOption(newOption);
    setError(null);
  };

  const handleImageUpload = async (event) => {
    const files = Array.from(event.target.files);
    event.target.value = "";
    if (!files.length) return;

    setIsUploading(true);
    setError(null);

    let newPairs = [];

    try {
      const token = localStorage.getItem("token");

      newPairs = await Promise.all(
        files.map(async (file) => {
          const id = Date.now() + "-" + Math.random().toString(36).substr(2, 9);
          const originalKey = id + "-original";
          await set(originalKey, file);
          return {
            id,
            fileName: file.name,
            originalKey,
            resultKey: null,
            original: URL.createObjectURL(file),
            result: null,
            classes: [],
            loading: true,
          };
        })
      );

      const updatedPairs = [...imagePairs, ...newPairs];
      setImagePairs(updatedPairs);
      saveImageMetadata(updatedPairs);

      const response = await uploadImagesForDetection(token, files);

      if (!response || !response.batch_id || !response.results) {
        throw new Error("Invalid API response format");
      }

      const { batch_id, results } = response;
      const defectResponse = await getDefectDetails(token, batch_id);

      let defectDetails = [];
      if (Array.isArray(defectResponse)) {
        defectDetails = defectResponse;
      } else if (defectResponse && Array.isArray(defectResponse.results)) {
        defectDetails = defectResponse.results;
      } else {
        throw new Error("Invalid defect details format");
      }

      const finalPairs = await Promise.all(
        updatedPairs.map(async (pair) => {
          const newPairIndex = newPairs.findIndex((np) => np.id === pair.id);
          if (newPairIndex !== -1) {
            const result = results[newPairIndex] || {};
            const defectDetail = defectDetails[newPairIndex] || { class_names: [] };

            if (!result.annotated_url) {
              console.warn("No result URL for", pair.fileName);
              return {
                ...pair,
                loading: false,
                error: "No result available",
              };
            }

            try {
              const annotatedResponse = await fetch(result.annotated_url);
              if (!annotatedResponse.ok) {
                throw new Error(`Failed to fetch image: ${annotatedResponse.status}`);
              }
              const blob = await annotatedResponse.blob();
              const resultKey = pair.id + "-result";
              await set(resultKey, blob);

              return {
                ...pair,
                resultKey,
                result: URL.createObjectURL(blob),
                classes: defectDetail.class_names || [],
                loading: false,
              };
            } catch (err) {
              console.error("Error fetching result image:", err);
              return {
                ...pair,
                loading: false,
                error: err.message || "Failed to load result",
              };
            }
          }
          return pair;
        })
      );

      setImagePairs(finalPairs);
      saveImageMetadata(finalPairs);
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "Failed to process images");

      if (newPairs.length > 0) {
        setImagePairs((prevPairs) =>
          prevPairs.map((pair) =>
            newPairs.some((np) => np.id === pair.id)
              ? { ...pair, loading: false, error: err.message }
              : pair
          )
        );
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleVideoUpload = async (event) => {
    const file = event.target.files[0];
    event.target.value = "";
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      const response = await uploadVideoForDetection(token, file);

      if (!response || !response.batch_id) {
        throw new Error("Invalid API response format");
      }

      const defectResponse = await getVideoDefectDetails(token, response.batch_id);
      const processedResults = {
        ...response,
        defectDetails: Array.isArray(defectResponse) ? defectResponse : [],
      };

      setVideoResults(processedResults);
      saveVideoMetadata(processedResults);
    } catch (err) {
      console.error("Video upload error:", err);
      setError(err.message || "Failed to process video");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeletePair = async (id) => {
    const pairToDelete = imagePairs.find((p) => p.id === id);
    if (pairToDelete) {
      await del(pairToDelete.originalKey);
      if (pairToDelete.resultKey) {
        await del(pairToDelete.resultKey);
      }
    }
    const updatedPairs = imagePairs.filter((pair) => pair.id !== id);
    setImagePairs(updatedPairs);
    saveImageMetadata(updatedPairs);
  };

  const handleClearAll = async () => {
    if (selectedOption === "image") {
      await Promise.all(
        imagePairs.map(async (pair) => {
          await del(pair.originalKey);
          if (pair.resultKey) {
            await del(pair.resultKey);
          }
        })
      );
      localStorage.removeItem("detectionImagePairs");
      setImagePairs([]);
    } else if (selectedOption === "video") {
      localStorage.removeItem("detectionVideoResults");
      setVideoResults(null);
    }
  };

  const renderImageView = () => {
    if (isUploading && imagePairs.length === 0) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" p={2}>
          <CircularProgress />
          <Typography variant="body2" sx={{ ml: 1 }}>
            Processing images...
          </Typography>
        </Box>
      );
    }

    if (error) {
      return (
        <Paper className="detection-data-box error">
          <Typography variant="subtitle1" className="detection-data-title">
            Error
          </Typography>
          <Typography variant="body2" color="error">
            {error}
          </Typography>
        </Paper>
      );
    }

    if (imagePairs.length === 0) {
      return (
        <Paper className="detection-data-box">
          <Typography variant="subtitle1" className="detection-data-title">
            Image Detection Results
          </Typography>
          <Typography variant="body2">
            Upload images to detect damaged stitches.
          </Typography>
        </Paper>
      );
    }

    return (
      <Box className="image-grid-container">
        {imagePairs.map((pair) => (
          <Box key={pair.id} sx={{ width: "100%", mb: 3 }}>
            <Paper className="image-pair-container">
              <Box className="pair-header">
                <Typography variant="subtitle2" className="file-name">
                  {pair.fileName}
                </Typography>
                <IconButton
                  className="delete-button"
                  onClick={() => handleDeletePair(pair.id)}
                  size="small"
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Box>

              {pair.classes && pair.classes.length > 0 && (
                <Box sx={{ mb: 2, display: "flex", flexWrap: "wrap", gap: 1 }}>
                  {pair.classes.map((className, idx) => (
                    <Chip
                      key={idx}
                      label={className}
                      size="small"
                      sx={{
                        backgroundColor: getClassColor(className),
                        color: "white",
                        fontWeight: 500,
                      }}
                    />
                  ))}
                </Box>
              )}

              {pair.error && (
                <Typography color="error" variant="caption" sx={{ mb: 2, display: "block" }}>
                  {pair.error}
                </Typography>
              )}

              <Box className="image-comparison-container" sx={{
                display: "flex",
                flexDirection: { xs: "column", sm: "row" },
                gap: 2,
                width: "100%",
              }}>
                <Box className="image-container" sx={{ flex: 1 }}>
                  <Typography variant="caption" display="block" gutterBottom>
                    Original
                  </Typography>
                  {pair.original && (
                    <img
                      src={pair.original}
                      alt="Original"
                      className="detection-image"
                      style={{ height: "350px", objectFit: "contain" }}
                    />
                  )}
                </Box>

                <Box className="image-container" sx={{ flex: 1 }}>
                  <Typography variant="caption" display="block" gutterBottom>
                    Result
                  </Typography>
                  {pair.result ? (
                    <img
                      src={pair.result}
                      alt="Detection result"
                      className="detection-image"
                      style={{ height: "350px", objectFit: "contain" }}
                    />
                  ) : pair.loading ? (
                    <Box className="processing-placeholder">
                      <CircularProgress size={24} />
                      <Typography variant="caption">Processing...</Typography>
                    </Box>
                  ) : (
                    <Box className="processing-placeholder">
                      <Typography variant="caption" color="error">
                        Failed to load result
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            </Paper>
          </Box>
        ))}
      </Box>
    );
  };

  const renderVideoView = () => {
    if (isUploading && !videoResults) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" p={2}>
          <CircularProgress />
          <Typography variant="body2" sx={{ ml: 1 }}>
            Processing video...
          </Typography>
        </Box>
      );
    }

    if (error) {
      return (
        <Paper className="detection-data-box error">
          <Typography variant="subtitle1" className="detection-data-title">
            Error
          </Typography>
          <Typography variant="body2" color="error">
            {error}
          </Typography>
        </Paper>
      );
    }

    if (!videoResults) {
      return (
        <Paper className="detection-data-box">
          <Typography variant="subtitle1" className="detection-data-title">
            Video Detection Results
          </Typography>
          <Typography variant="body2">
            Upload a video to analyze all detected frames.
          </Typography>
        </Paper>
      );
    }

    return (
      <Box className="video-results-container">
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Video Analysis Summary
          </Typography>
          <Box sx={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
            <Typography>
              <strong>Total Frames:</strong> {videoResults.total_frames}
            </Typography>
            <Typography>
              <strong>Defective Frames:</strong> {videoResults.defective_frames}
            </Typography>
            <Typography>
              <strong>Defect Rate:</strong>{" "}
              {((videoResults.defective_frames / videoResults.total_frames) * 100).toFixed(2)}%
            </Typography>
          </Box>
        </Paper>

        <Box className="video-frames-grid">
          {videoResults.defectDetails.map((frame, index) => (
            <Paper key={index} sx={{ p: 2, mb: 2 }}>
              <Box className="frame-header">
                <Typography variant="subtitle2">
                  Frame {frame.image_url.split("_").pop().replace(".jpg", "")}
                </Typography>
                {frame.class_names && frame.class_names.length > 0 && (
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 1 }}>
                    {frame.class_names.map((className, idx) => (
                      <Chip
                        key={idx}
                        label={className}
                        size="small"
                        sx={{
                          backgroundColor: getClassColor(className),
                          color: "white",
                          fontWeight: 500,
                        }}
                      />
                    ))}
                  </Box>
                )}
              </Box>
              <img
                src={frame.image_url || ''}
                alt={`Frame ${index}`}
                style={{
                  width: "100%",
                  maxHeight: "300px",
                  objectFit: "contain",
                }}
                onError={(e) => {
                  console.error('Failed to load image:', frame.image_url);
                  e.target.style.display = 'none';
                }}
              />
            </Paper>
          ))}
        </Box>
      </Box>
    );
  };

  const renderCurrentView = () => {
    switch (selectedOption) {
      case "image":
        return renderImageView();
      case "video":
        return renderVideoView();
      default:
        return null;
    }
  };

  return (
    <div className="detection-container">
      <Box className="detection-dropdown-container">
        <Box display="flex" alignItems="center" gap={2}>
          <FormControl fullWidth size="small" sx={{ flex: 1 }}>
            <Select
              value={selectedOption}
              onChange={handleChange}
              className="detection-dropdown"
            >
              <MenuItem value="image">🖼️ Image Upload</MenuItem>
              <MenuItem value="video">🎥 Video Upload</MenuItem>
            </Select>
          </FormControl>
          {((selectedOption === "image" && imagePairs.length > 0) ||
            (selectedOption === "video" && videoResults)) && (
            <Button
              variant="outlined"
              color="error"
              onClick={handleClearAll}
              size="small"
              startIcon={<DeleteIcon fontSize="small" />}
              sx={{
                whiteSpace: "nowrap",
                minWidth: "fit-content",
              }}
            >
              Clear All
            </Button>
          )}
        </Box>
      </Box>

      <CardContent className="detection-card-content">
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {selectedOption === "image" &&
            "Upload images to detect damaged stitches."}
          {selectedOption === "video" &&
            "Upload a video to analyze all detected frames."}
        </Typography>

        {selectedOption === "image" && (
          <Box mb={2}>
            <input
              accept="image/*"
              style={{ display: "none" }}
              id="raised-button-file"
              multiple
              type="file"
              onChange={handleImageUpload}
            />
            <label htmlFor="raised-button-file">
              <Button variant="contained" component="span">
                Upload Images
              </Button>
            </label>
          </Box>
        )}

        {selectedOption === "video" && (
          <Box mb={2}>
            <input
              accept="video/*"
              style={{ display: "none" }}
              id="video-upload-button"
              type="file"
              onChange={handleVideoUpload}
            />
            <label htmlFor="video-upload-button">
              <Button variant="contained" component="span">
                Upload Video
              </Button>
            </label>
          </Box>
        )}

        {renderCurrentView()}
      </CardContent>
    </div>
  );
};

export default DetectionDashboard;