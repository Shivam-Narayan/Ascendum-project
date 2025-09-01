import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  uploadImages,
  saveAnnotations,
  trainModel,
} from "../../../Services/TrainingModuleApi";
import "./trainingmodeldashboard.css";
import {
  Tabs,
  Tab,
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  CircularProgress,
  Snackbar,
  Alert,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  Avatar,
} from "@mui/material";
import {
  ArrowBackIos,
  ArrowForwardIos,
  Close,
  RectangleOutlined,
  Save,
  Cancel,
  Download,
  Visibility,
  Info,
  PhotoLibrary,
  Collections,
  Category,
  Schedule,
} from "@mui/icons-material";

const TrainingModelDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [images, setImages] = useState([]);
  const [annotatedImages, setAnnotatedImages] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isExpanded, setIsExpanded] = useState(true);
  const [namesStartIndex, setNamesStartIndex] = useState(0);
  const [isDrawing, setIsDrawing] = useState(false);
  const [boxes, setBoxes] = useState([]);
  const [currentBox, setCurrentBox] = useState(null);
  const [classes, setClasses] = useState([
    "Person",
    "Vehicle",
    "Animal",
    "Object",
  ]);
  const [newClass, setNewClass] = useState("");
  const [selectedClass, setSelectedClass] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isSavingAnnotations, setIsSavingAnnotations] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);

  const canvasRef = useRef(null);
  const imageRef = useRef(null);

  const [trainingParams, setTrainingParams] = useState({
    epochs: 10,
    batchSize: 8,
    learningRate: 0.001,
  });
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState(null);

  const handleTrainModel = async () => {
    if (images.length === 0) {
      showSnackbar("No images available for training", "error");
      return;
    }

    setIsTraining(true);
    try {
      const token = localStorage.getItem("token");
      const response = await trainModel(trainingParams.epochs, token);

      setTrainingResult(response);
      showSnackbar(response.message || "Model training started successfully");
    } catch (error) {
      console.error("Error training model:", error);
      showSnackbar(error.message || "Failed to start model training", "error");
    } finally {
      setIsTraining(false);
    }
  };

  const handleParamChange = (param, value) => {
    setTrainingParams((prev) => ({
      ...prev,
      [param]: value,
    }));
  };

  // Load saved images from localStorage on component mount
  useEffect(() => {
    const savedImages = localStorage.getItem("annotatedImages");
    const savedAnnotatedImages = localStorage.getItem(
      "persistedAnnotatedImages"
    );

    if (savedImages) {
      setImages(JSON.parse(savedImages));
      if (JSON.parse(savedImages).length > 0) {
        setIsExpanded(false);
      }
    }

    if (savedAnnotatedImages) {
      setAnnotatedImages(JSON.parse(savedAnnotatedImages));
    }
  }, []);

  // Save images to localStorage whenever they change
  useEffect(() => {
    if (images.length > 0) {
      localStorage.setItem("annotatedImages", JSON.stringify(images));
    } else {
      localStorage.removeItem("annotatedImages");
    }

    // When images are annotated, add them to the annotatedImages list
    const newlyAnnotated = images.filter((img) => img.annotations?.length > 0);
    if (newlyAnnotated.length > 0) {
      const uniqueAnnotated = [
        ...new Map([
          ...annotatedImages.map((item) => [item.url, item]),
          ...newlyAnnotated.map((item) => [item.url, item]),
        ]).values(),
      ];

      setAnnotatedImages(uniqueAnnotated);
    }
  }, [images, annotatedImages]);

  useEffect(() => {
    if (annotatedImages.length > 0) {
      localStorage.setItem(
        "persistedAnnotatedImages",
        JSON.stringify(annotatedImages)
      );
    }
  }, [annotatedImages]);

  const showSnackbar = (message, severity = "success") => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleFiles = async (files) => {
    const validImages = Array.from(files).filter((file) =>
      ["image/jpeg", "image/png", "image/jpg"].includes(file.type)
    );

    if (validImages.length === 0) {
      showSnackbar("No valid images found (only JPG/PNG allowed)", "error");
      return;
    }

    setIsUploading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await uploadImages(validImages, token);

      const newImages = validImages.map((file, index) => {
        const serverImage = response.images[index] || {};
        return {
          file,
          url: serverImage.image_url || URL.createObjectURL(file),
          name:
            file.name.length > 15
              ? `${file.name.substring(0, 12)}...`
              : file.name,
          annotations: [],
          imageId: serverImage.image_id,
          timestamp: new Date().toISOString(),
        };
      });

      setImages((prev) => [...prev, ...newImages]);
      if (images.length === 0 && newImages.length > 0) {
        setCurrentIndex(0);
        setIsExpanded(false);
      }
      showSnackbar(`${validImages.length} images uploaded successfully`);
    } catch (error) {
      console.error("Error uploading images:", error);
      showSnackbar(
        "Failed to upload images. Using local storage instead.",
        "warning"
      );

      const newImages = validImages.map((file) => ({
        file,
        url: URL.createObjectURL(file),
        name:
          file.name.length > 15
            ? `${file.name.substring(0, 12)}...`
            : file.name,
        annotations: [],
        timestamp: new Date().toISOString(),
      }));
      setImages((prev) => [...prev, ...newImages]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  const handleBrowse = (e) => {
    handleFiles(e.target.files);
    e.target.value = ""; // Reset file input
  };

  const handlePrev = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
    setBoxes(images[Math.max(currentIndex - 1, 0)].annotations || []);
    setCurrentBox(null);
  };

  const handleNext = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, images.length - 1));
    setBoxes(
      images[Math.min(currentIndex + 1, images.length - 1)].annotations || []
    );
    setCurrentBox(null);
  };

  const handleNamesPrev = () => {
    setNamesStartIndex((prev) => Math.max(prev - 1, 0));
  };

  const handleNamesNext = () => {
    setNamesStartIndex((prev) => Math.min(prev + 1, images.length - 3));
  };

  const removeImage = (index) => {
    const updated = images.filter((_, i) => i !== index);
    setImages(updated);

    if (currentIndex >= updated.length) {
      setCurrentIndex(updated.length - 1);
    }

    if (updated.length === 0) {
      setIsExpanded(true);
    }
  };

  const removeCurrent = () => {
    removeImage(currentIndex);
  };

  const removeAll = () => {
    setImages([]);
    setCurrentIndex(0);
    setIsExpanded(true);
    setNamesStartIndex(0);
  };

  const startDrawing = () => {
    if (!selectedClass && classes.length > 0) {
      setSelectedClass(classes[0]);
    }
    setIsDrawing(true);
  };

  const cancelDrawing = () => {
    setIsDrawing(false);
    setCurrentBox(null);
  };

  const saveBox = async () => {
    if (
      !currentBox ||
      Math.abs(currentBox.width) < 10 ||
      Math.abs(currentBox.height) < 10
    ) {
      showSnackbar(
        "Annotation too small. Please draw a larger box.",
        "warning"
      );
      return;
    }

    const img = imageRef.current;
    const displayedW = img.width;
    const displayedH = img.height;

    const normalizedBox = {
      x: Math.min(currentBox.x, currentBox.x + currentBox.width) / displayedW,
      y: Math.min(currentBox.y, currentBox.y + currentBox.height) / displayedH,
      width: Math.abs(currentBox.width) / displayedW,
      height: Math.abs(currentBox.height) / displayedH,
      class: selectedClass || classes[0],
    };

    const updatedImages = [...images];
    updatedImages[currentIndex].annotations = [...boxes, normalizedBox];
    setImages(updatedImages);
    setBoxes(updatedImages[currentIndex].annotations);

    if (updatedImages[currentIndex].imageId) {
      setIsSavingAnnotations(true);
      try {
        const token = localStorage.getItem("token");
        await saveAnnotations(
          updatedImages[currentIndex].imageId,
          updatedImages[currentIndex].annotations,
          token
        );
        showSnackbar("Annotation saved successfully");
      } catch (error) {
        console.error("Failed to save annotations:", error);
        showSnackbar("Failed to save annotation to server", "error");
      } finally {
        setIsSavingAnnotations(false);
      }
    }

    setIsDrawing(false);
    setCurrentBox(null);
  };

  const handleMouseDown = (e) => {
    if (
      !isDrawing ||
      !imageRef.current ||
      (e.type === "mousedown" && e.button !== 0)
    )
      return;
    const rect = imageRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const y = Math.max(0, Math.min(e.clientY - rect.top, rect.height));

    setCurrentBox({
      x,
      y,
      width: 0,
      height: 0,
      class: selectedClass || classes[0],
    });
  };

  const handleMouseMove = (e) => {
    if (!isDrawing || !currentBox || !imageRef.current) return;

    const rect = imageRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const y = Math.max(0, Math.min(e.clientY - rect.top, rect.height));

    setCurrentBox((prev) => ({
      ...prev,
      width: x - prev.x,
      height: y - prev.y,
    }));
  };

  const handleMouseUp = () => {
    if (isDrawing && currentBox) {
      saveBox();
    }
  };

  const handleTouchStart = (e) => {
    if (!isDrawing || !imageRef.current) return;
    e.preventDefault(); // Prevent scrolling/zooming
    const touch = e.touches[0];
    const rect = imageRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(touch.clientX - rect.left, rect.width));
    const y = Math.max(0, Math.min(touch.clientY - rect.top, rect.height));
    setCurrentBox({
      x,
      y,
      width: 0,
      height: 0,
      class: selectedClass || classes[0],
    });
  };

  const handleTouchMove = (e) => {
    if (!isDrawing || !currentBox || !imageRef.current) return;
    e.preventDefault(); // Prevent scrolling/zooming
    const touch = e.touches[0];
    const rect = imageRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(touch.clientX - rect.left, rect.width));
    const y = Math.max(0, Math.min(touch.clientY - rect.top, rect.height));
    setCurrentBox((prev) => ({
      ...prev,
      width: x - prev.x,
      height: y - prev.y,
    }));
  };

  const handleTouchEnd = () => {
    if (isDrawing && currentBox) {
      saveBox();
    }
  };

  const handleContextMenu = (e) => {
    e.preventDefault();
    if (isDrawing) cancelDrawing();
  };

  const addNewClass = () => {
    if (!newClass.trim()) {
      showSnackbar("Class name cannot be empty", "error");
      return;
    }
    if (classes.includes(newClass.trim())) {
      showSnackbar("Class already exists", "error");
      return;
    }

    setClasses([...classes, newClass.trim()]);
    setSelectedClass(newClass.trim());
    setNewClass("");
    showSnackbar(`Class "${newClass.trim()}" added`);
  };

  const removeAnnotation = (index) => {
    const updatedImages = [...images];
    updatedImages[currentIndex].annotations = boxes.filter(
      (_, i) => i !== index
    );
    setImages(updatedImages);
    setBoxes(updatedImages[currentIndex].annotations);
    showSnackbar("Annotation removed");
  };

  const clearAllAnnotations = () => {
    const updatedImages = [...images];
    updatedImages[currentIndex].annotations = [];
    setImages(updatedImages);
    setBoxes([]);
    showSnackbar("All annotations cleared");
  };

  const downloadImage = (imageUrl, imageName) => {
    // Find the image in our state to get annotations
    const imageData =
      annotatedImages.find((img) => img.url === imageUrl) ||
      images.find((img) => img.url === imageUrl);

    if (!imageData) {
      showSnackbar("Image data not found", "error");
      return;
    }

    const img = new Image();
    img.crossOrigin = "Anonymous";
    img.onload = () => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      // Set canvas to image dimensions
      canvas.width = img.width;
      canvas.height = img.height;

      // Draw the original image
      ctx.drawImage(img, 0, 0);

      // Draw annotations if they exist
      if (imageData.annotations?.length > 0) {
        ctx.strokeStyle = "#FF0000";
        ctx.lineWidth = 2;
        ctx.font = "12px Arial";
        ctx.fillStyle = "#FF0000";

        imageData.annotations.forEach((box) => {
          const x = box.x * canvas.width;
          const y = box.y * canvas.height;
          const width = box.width * canvas.width;
          const height = box.height * canvas.height;

          // Draw bounding box
          ctx.strokeRect(x, y, width, height);

          // Draw class label
          ctx.fillText(box.class, x + 5, y + 15);
        });
      }

      // Convert canvas to blob and download
      canvas.toBlob(
        (blob) => {
          const link = document.createElement("a");
          const url = URL.createObjectURL(blob);
          const extension = imageUrl.split(".").pop().split("?")[0] || "jpg";
          link.href = url;
          link.download = `${imageName || "annotated-image"}.${extension}`;

          document.body.appendChild(link);
          link.click();

          // Clean up
          setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
          }, 100);
        },
        "image/jpeg",
        0.95
      );
    };

    img.onerror = () => {
      showSnackbar("Failed to load image for download", "error");
    };

    img.src = imageUrl;
  };

  const openPreview = (image) => {
    setPreviewImage(image);
    setPreviewOpen(true);
  };

  const closePreview = () => {
    setPreviewOpen(false);
    setPreviewImage(null);
  };

  const drawBoxes = useCallback(() => {
    if (!canvasRef.current || !imageRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const img = imageRef.current;

    canvas.width = img.width;
    canvas.height = img.height;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw existing boxes (normalized)
    boxes.forEach((box) => {
      const x = box.x * canvas.width;
      const y = box.y * canvas.height;
      const width = box.width * canvas.width;
      const height = box.height * canvas.height;

      ctx.strokeStyle = "#FF0000";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, width, height);
      ctx.fillStyle = "#FF0000";
      ctx.font = "12px Arial";
      ctx.fillText(box.class, x + 5, y + 15);
    });

    // Draw current box being drawn (still in pixels)
    if (currentBox) {
      const x =
        currentBox.width < 0 ? currentBox.x + currentBox.width : currentBox.x;
      const y =
        currentBox.height < 0 ? currentBox.y + currentBox.height : currentBox.y;
      const width = Math.abs(currentBox.width);
      const height = Math.abs(currentBox.height);

      ctx.strokeStyle = "#00FF00";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, width, height);
      ctx.fillStyle = "#00FF00";
      ctx.font = "12px Arial";
      ctx.fillText(currentBox.class, x + 5, y + 15);
    }
  }, [boxes, currentBox]);

  useEffect(() => {
    drawBoxes();
  }, [drawBoxes]);

  useEffect(() => {
    if (images.length > 0 && currentIndex < images.length) {
      setBoxes(images[currentIndex].annotations || []);
    }
  }, [currentIndex, images]);

  return (
    <div className="training-container">
      <Box className="tabs-wrapper">
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          indicatorColor="primary"
          textColor="primary"
          className="tab-bar"
        >
          <Tab label="Upload & Annotate" />
          <Tab label="View Annotations" />
          <Tab label="Train Model" />
        </Tabs>

        <Box className="tab-content">
          {activeTab === 0 && (
            <Box>
              <div
                className={`drop-zone ${isExpanded ? "expanded" : "compact"}`}
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
              >
                {isExpanded && (
                  <Typography variant="body2">
                    Drag & drop files here
                  </Typography>
                )}

                <input
                  type="file"
                  accept="image/jpeg,image/png,image/jpg"
                  multiple
                  onChange={handleBrowse}
                  id="file-input"
                  style={{ display: "none" }}
                />

                <Button
                  variant="contained"
                  className={`browse-btn ${isExpanded ? "" : "small"}`}
                  component="label"
                  htmlFor="file-input"
                  disabled={isUploading}
                >
                  {isUploading ? (
                    <>
                      <CircularProgress
                        size={20}
                        color="inherit"
                        sx={{ mr: 1 }}
                      />
                      Uploading...
                    </>
                  ) : (
                    "Browse Files"
                  )}
                </Button>
              </div>

              {images.length > 0 && (
                <>
                  <Box className="image-names-container">
                    {namesStartIndex > 0 && (
                      <IconButton
                        onClick={handleNamesPrev}
                        size="small"
                        className="names-nav-button"
                      >
                        <ArrowBackIos fontSize="small" />
                      </IconButton>
                    )}

                    <Box className="image-names">
                      {images
                        .slice(namesStartIndex, namesStartIndex + 3)
                        .map((image, index) => (
                          <Chip
                            key={namesStartIndex + index}
                            label={image.name}
                            onDelete={() =>
                              removeImage(namesStartIndex + index)
                            }
                            deleteIcon={<Close />}
                            variant={
                              currentIndex === namesStartIndex + index
                                ? "filled"
                                : "outlined"
                            }
                            color={
                              currentIndex === namesStartIndex + index
                                ? "primary"
                                : "default"
                            }
                            onClick={() =>
                              setCurrentIndex(namesStartIndex + index)
                            }
                            className="image-name-chip"
                          />
                        ))}
                    </Box>

                    {namesStartIndex + 3 < images.length && (
                      <IconButton
                        onClick={handleNamesNext}
                        size="small"
                        className="names-nav-button"
                      >
                        <ArrowForwardIos fontSize="small" />
                      </IconButton>
                    )}
                  </Box>

                  <Box className="preview-section">
                    <div className="image-container">
                      <img
                        ref={imageRef}
                        src={images[currentIndex]?.url}
                        alt={`Preview ${currentIndex + 1}`}
                        className="preview-image"
                        onLoad={drawBoxes}
                        onMouseDown={handleMouseDown}
                        onMouseMove={handleMouseMove}
                        onMouseUp={handleMouseUp}
                        onContextMenu={handleContextMenu}
                        onTouchStart={handleTouchStart}
                        onTouchMove={handleTouchMove}
                        onTouchEnd={handleTouchEnd}
                        style={{
                          cursor: isDrawing ? "crosshair" : "default",
                          touchAction: isDrawing ? "none" : "auto",
                        }}
                      />
                      <canvas
                        ref={canvasRef}
                        className="annotation-canvas"
                        style={{ position: "absolute", pointerEvents: "none" }}
                      />
                    </div>

                    <Typography variant="body2" className="image-count">
                      Image {currentIndex + 1} of {images.length} | Annotations:{" "}
                      {boxes.length}
                    </Typography>

                    <Box className="nav-buttons">
                      <IconButton
                        onClick={handlePrev}
                        disabled={currentIndex === 0}
                      >
                        <ArrowBackIos />
                      </IconButton>
                      <IconButton
                        onClick={handleNext}
                        disabled={currentIndex === images.length - 1}
                      >
                        <ArrowForwardIos />
                      </IconButton>
                    </Box>

                    <Box className="annotation-controls">
                      <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Class</InputLabel>
                        <Select
                          value={selectedClass}
                          label="Class"
                          onChange={(e) => setSelectedClass(e.target.value)}
                          sx={{
                            borderRadius: "8px",
                            backgroundColor: "white",
                            "& .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#00acc1",
                            },
                          }}
                        >
                          {classes.map((cls) => (
                            <MenuItem key={cls} value={cls}>
                              {cls}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>

                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <TextField
                          size="small"
                          label="New Class"
                          value={newClass}
                          onChange={(e) => setNewClass(e.target.value)}
                          onKeyPress={(e) => e.key === "Enter" && addNewClass()}
                          sx={{ width: 150 }}
                        />
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={addNewClass}
                        >
                          Add
                        </Button>
                      </Box>

                      {!isDrawing ? (
                        <Button
                          variant="contained"
                          startIcon={<RectangleOutlined />}
                          onClick={startDrawing}
                          disabled={classes.length === 0}
                        >
                          Draw Box
                        </Button>
                      ) : (
                        <>
                          <Button
                            variant="contained"
                            color="success"
                            startIcon={<Save />}
                            onClick={saveBox}
                            disabled={isSavingAnnotations}
                          >
                            {isSavingAnnotations ? (
                              <>
                                <CircularProgress
                                  size={20}
                                  color="inherit"
                                  sx={{ mr: 1 }}
                                />
                                Saving...
                              </>
                            ) : (
                              "Save"
                            )}
                          </Button>
                          <Button
                            variant="outlined"
                            color="error"
                            startIcon={<Cancel />}
                            onClick={cancelDrawing}
                          >
                            Cancel
                          </Button>
                        </>
                      )}

                      {boxes.length > 0 && (
                        <Button
                          variant="outlined"
                          color="error"
                          onClick={clearAllAnnotations}
                        >
                          Clear All
                        </Button>
                      )}
                    </Box>

                    {boxes.length > 0 && (
                      <Box className="annotations-list">
                        <Typography variant="subtitle2">
                          Annotations:
                        </Typography>
                        <Box
                          sx={{
                            display: "flex",
                            flexWrap: "wrap",
                            gap: 1,
                            mt: 1,
                          }}
                        >
                          {boxes.map((box, index) => (
                            <Chip
                              key={index}
                              label={`${box.class} (${Math.round(
                                box.width * 100
                              )}%x${Math.round(box.height * 100)}%)`}
                              onDelete={() => removeAnnotation(index)}
                              variant="outlined"
                              color="primary"
                            />
                          ))}
                        </Box>
                      </Box>
                    )}

                    <Box className="action-buttons">
                      <Button
                        variant="outlined"
                        color="error"
                        onClick={removeCurrent}
                      >
                        Remove Current
                      </Button>
                      <Button
                        variant="contained"
                        color="error"
                        onClick={removeAll}
                      >
                        Remove All
                      </Button>
                    </Box>
                  </Box>
                </>
              )}
            </Box>
          )}

          {activeTab === 1 && (
            <Box className="view-annotations">
              {annotatedImages.length > 0 ? (
                <>
                  <Paper
                    elevation={0}
                    className="dataset-summary"
                    sx={{
                      p: 3,
                      mb: 4,
                      background:
                        "linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)",
                      borderRadius: "16px",
                      border: "1px solid rgba(0, 172, 193, 0.2)",
                    }}
                  >
                    <Typography
                      variant="h5"
                      gutterBottom
                      className="summary-title"
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        color: "#004d40",
                        fontWeight: 600,
                        mb: 3,
                        pb: 1,
                        borderBottom: "2px solid #b2dfdb",
                      }}
                    >
                      <Info color="primary" sx={{ mr: 1.5 }} />
                      Dataset Summary
                    </Typography>
                    <Grid container spacing={3}>
                      {[
                        {
                          title: "Total Images",
                          value: annotatedImages.length,
                          icon: <PhotoLibrary />,
                          color: "#4caf50",
                        },
                        {
                          title: "Total Annotations",
                          value: annotatedImages.reduce(
                            (acc, img) => acc + (img.annotations?.length || 0),
                            0
                          ),
                          icon: <Collections />,
                          color: "#2196f3",
                        },
                        {
                          title: "Unique Classes",
                          value: Array.from(
                            new Set(
                              annotatedImages.flatMap(
                                (img) =>
                                  img.annotations?.map((ann) => ann.class) || []
                              )
                            )
                          ).length,
                          icon: <Category />,
                          color: "#ff9800",
                        },
                        {
                          title: "Last Updated",
                          value: new Date(
                            annotatedImages[0]?.timestamp
                          ).toLocaleDateString(),
                          icon: <Schedule />,
                          color: "#9c27b0",
                        },
                      ].map((item, index) => (
                        <Grid item xs={12} sm={6} md={3} key={index}>
                          <Paper
                            elevation={0}
                            sx={{
                              p: 2,
                              height: "100%",
                              borderRadius: "12px",
                              background: "white",
                              boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
                              borderLeft: `4px solid ${item.color}`,
                              transition: "transform 0.3s, box-shadow 0.3s",
                              "&:hover": {
                                transform: "translateY(-4px)",
                                boxShadow: "0 8px 25px rgba(0, 0, 0, 0.12)",
                              },
                            }}
                          >
                            <Box display="flex" alignItems="center">
                              <Avatar
                                sx={{
                                  bgcolor: `${item.color}20`,
                                  color: item.color,
                                  mr: 2,
                                  width: 48,
                                  height: 48,
                                }}
                              >
                                {item.icon}
                              </Avatar>
                              <Box>
                                <Typography
                                  variant="subtitle2"
                                  color="text.secondary"
                                >
                                  {item.title}
                                </Typography>
                                <Typography
                                  variant="h5"
                                  fontWeight="bold"
                                  color="text.primary"
                                >
                                  {item.value}
                                </Typography>
                              </Box>
                            </Box>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </Paper>

                  <Typography
                    variant="h6"
                    gutterBottom
                    className="images-title"
                  >
                    Annotated Images
                  </Typography>
                  <Box sx={{ display: "flex", justifyContent: "center" }}>
                    <Grid
                      container
                      spacing={3}
                      sx={{ maxWidth: "100%", width: "100%" }}
                    >
                      {annotatedImages.map((image, index) => (
                        <Grid
                          item
                          xs={12}
                          sm={6}
                          md={4}
                          key={index}
                          sx={{ display: "flex" }}
                        >
                          <Card
                            sx={{
                              width: "100%",
                              display: "flex",
                              flexDirection: "column",
                              borderRadius: "16px",
                              overflow: "hidden",
                              boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
                              transition:
                                "transform 0.3s ease, box-shadow 0.3s ease",
                              "&:hover": {
                                transform: "translateY(-5px)",
                                boxShadow: "0 10px 20px rgba(0, 0, 0, 0.15)",
                              },
                            }}
                          >
                            <Box
                              sx={{
                                position: "relative",
                                paddingTop: "56.25%", // 16:9 aspect ratio
                                overflow: "hidden",
                              }}
                            >
                              <CardMedia
                                component="img"
                                image={image.url}
                                alt={image.name}
                                onClick={() => openPreview(image)}
                                sx={{
                                  position: "absolute",
                                  top: 0,
                                  left: 0,
                                  width: "100%",
                                  height: "100%",
                                  objectFit: "cover",
                                  cursor: "pointer",
                                  transition: "opacity 0.3s ease",
                                  "&:hover": {
                                    opacity: 0.9,
                                  },
                                }}
                              />
                            </Box>
                            <CardContent sx={{ flexGrow: 1 }}>
                              <Typography
                                gutterBottom
                                variant="subtitle1"
                                noWrap
                              >
                                {image.name}
                              </Typography>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                {image.annotations?.length || 0} annotation(s)
                              </Typography>
                              {image.annotations?.length > 0 && (
                                <Box sx={{ mt: 1 }}>
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                  >
                                    Classes:
                                  </Typography>
                                  <Box
                                    sx={{
                                      display: "flex",
                                      flexWrap: "wrap",
                                      gap: 0.5,
                                      mt: 0.5,
                                    }}
                                  >
                                    {Array.from(
                                      new Set(
                                        image.annotations.map((a) => a.class)
                                      )
                                    ).map((cls, i) => (
                                      <Chip
                                        key={i}
                                        label={cls}
                                        size="small"
                                        color="primary"
                                        variant="outlined"
                                      />
                                    ))}
                                  </Box>
                                </Box>
                              )}
                            </CardContent>
                            <CardActions
                              sx={{
                                justifyContent: "space-between",
                                borderTop: "1px solid rgba(0, 0, 0, 0.12)",
                              }}
                            >
                              <Button
                                size="small"
                                startIcon={<Visibility />}
                                onClick={() => openPreview(image)}
                                color="primary"
                              >
                                Preview
                              </Button>
                              <Button
                                size="small"
                                startIcon={<Download />}
                                onClick={() =>
                                  downloadImage(image.url, image.name)
                                }
                                color="secondary"
                              >
                                Download
                              </Button>
                            </CardActions>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                </>
              ) : (
                <Box className="no-data">
                  <Typography variant="h6" color="textSecondary" gutterBottom>
                    No annotated images found
                  </Typography>
                  <Typography
                    variant="body1"
                    color="textSecondary"
                    sx={{ mb: 2 }}
                  >
                    Upload and annotate images in the "Upload & Annotate" tab
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => setActiveTab(0)}
                    className="action-button"
                  >
                    Go to Upload
                  </Button>
                </Box>
              )}
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              {images.length > 0 ? (
                <Box>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 4,
                      mb: 4,
                      borderRadius: "16px",
                      background:
                        "linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)",
                      border: "1px solid rgba(0, 172, 193, 0.2)",
                    }}
                  >
                    <Typography
                      variant="h5"
                      gutterBottom
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        color: "#004d40",
                        fontWeight: 600,
                        mb: 3,
                        pb: 1,
                        borderBottom: "2px solid #b2dfdb",
                      }}
                    >
                      <Info color="primary" sx={{ mr: 1.5 }} />
                      Training Configuration
                    </Typography>

                    <Grid container spacing={4}>
                      <Grid item xs={12} md={6}>
                        <Paper
                          elevation={0}
                          sx={{
                            p: 3,
                            height: "300px",
                            width:"200px",
                            display: "inline-block",
                            borderRadius: "12px",
                            backgroundColor: "white",
                            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
                          }}
                        >
                          <Typography
                            variant="h6"
                            gutterBottom
                            sx={{
                              color: "#00796b",
                              fontWeight: 500,
                              mb: 2,
                            }}
                          >
                            Dataset Statistics
                          </Typography>
                          <List dense>
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText
                                primary="Total Images"
                                primaryTypographyProps={{ fontWeight: 500 }}
                                secondary={images.length}
                                secondaryTypographyProps={{
                                  color: "text.primary",
                                  fontWeight: 600,
                                }}
                              />
                            </ListItem>
                            <Divider />
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText
                                primary="Total Annotations"
                                primaryTypographyProps={{ fontWeight: 500 }}
                                secondary={images.reduce(
                                  (acc, img) =>
                                    acc + (img.annotations?.length || 0),
                                  0
                                )}
                                secondaryTypographyProps={{
                                  color: "text.primary",
                                  fontWeight: 600,
                                }}
                              />
                            </ListItem>
                            <Divider />
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText
                                primary="Classes"
                                primaryTypographyProps={{ fontWeight: 500 }}
                                secondary={(() => {
                                  const classes = Array.from(
                                    new Set(
                                      images.flatMap(
                                        (img) =>
                                          img.annotations?.map(
                                            (ann) => ann.class
                                          ) || []
                                      )
                                    )
                                  );
                                  return classes.length > 0
                                    ? classes.join(", ")
                                    : "No classes defined";
                                })()}
                                secondaryTypographyProps={{
                                  color: "text.primary",
                                  fontWeight: 600,
                                }}
                              />
                            </ListItem>
                          </List>
                        </Paper>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Paper
                          elevation={0}
                          sx={{
                            p: 3,
                            width: "472px",
                            margin: "0 auto",
                            height: "300px",
                            display: "inline-block",
                            borderRadius: "12px",
                            backgroundColor: "white",
                            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
                          }}
                        >
                          <Typography
                            variant="h6"
                            gutterBottom
                            sx={{
                              color: "#00796b",
                              fontWeight: 500,
                              mb: 2,
                            }}
                          >
                            Training Parameters
                          </Typography>

                          <TextField
                            fullWidth
                            label="Epochs"
                            type="number"
                            value={trainingParams.epochs}
                            onChange={(e) =>
                              handleParamChange(
                                "epochs",
                                parseInt(e.target.value) || 1
                              )
                            }
                            margin="normal"
                            variant="outlined"
                            InputProps={{ style: { borderRadius: "8px" } }}
                            sx={{ mb: 2 }}
                          />

                          <TextField
                            fullWidth
                            label="Batch Size"
                            type="number"
                            value={trainingParams.batchSize}
                            onChange={(e) =>
                              handleParamChange(
                                "batchSize",
                                parseInt(e.target.value) || 8
                              )
                            }
                            margin="normal"
                            variant="outlined"
                            InputProps={{ style: { borderRadius: "8px" } }}
                            sx={{ mb: 2 }}
                          />

                          <TextField
                            fullWidth
                            label="Learning Rate"
                            type="number"
                            value={trainingParams.learningRate}
                            onChange={(e) =>
                              handleParamChange(
                                "learningRate",
                                parseFloat(e.target.value) || 0.001
                              )
                            }
                            margin="normal"
                            variant="outlined"
                            inputProps={{ step: "0.0001" }}
                            InputProps={{ style: { borderRadius: "8px" } }}
                          />
                        </Paper>
                      </Grid>
                      {/* Knowledge Sharing (YAML Merge) */}
                      <Grid item xs={12} md={4}>
                        <Paper
                          elevation={0}
                          sx={{
                            p: 3,
                            height: "300px",
                            borderRadius: "12px",
                            backgroundColor: "white",
                            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
                            textAlign: "center",
                            width:"200px"
                          }}
                        >
                          <Typography
                            variant="h6"
                            gutterBottom
                            sx={{
                              color: "#00796b",
                              fontWeight: 500,
                              mb: 2,
                            }}
                          >
                            Knowledge Sharing
                          </Typography>

                          <Typography variant="body2" sx={{ mb: 2 }}>
                            Combine your new files with the existing ones to keep everything organized and easy to share across projects.
                          </Typography>

                          <Typography
                            variant="body2"
                            sx={{
                              color: "text.secondary",
                              fontStyle: "italic",
                              fontWeight: 500,
                              mb: 2,
                            }}
                          >
                            ⚠️ This feature will be available after subscription
                            or deployment.
                          </Typography>

                          <Button
                            variant="contained"
                            color="primary"
                            disabled
                            sx={{ borderRadius: "8px", textTransform: "none" }}
                          >
                            Join Files Together
                          </Button>
                        </Paper>
                      </Grid>
                    </Grid>
                  </Paper>

                  {trainingResult && (
                    <Paper
                      elevation={0}
                      sx={{
                        p: 3,
                        mb: 4,
                        borderRadius: "16px",
                        backgroundColor: "#e8f5e9",
                        border: "1px solid #a5d6a7",
                      }}
                    >
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ color: "#2e7d32" }}
                      >
                        Training Result
                      </Typography>
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        {trainingResult.message}
                      </Typography>
                      {trainingResult.yaml_path && (
                        <Typography
                          variant="body2"
                          sx={{ fontFamily: "monospace" }}
                        >
                          YAML Path: {trainingResult.yaml_path}
                        </Typography>
                      )}
                    </Paper>
                  )}

                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      mt: 4,
                      mb: 4,
                    }}
                  >
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handleTrainModel}
                      disabled={isTraining}
                      sx={{
                        px: 6,
                        py: 1.5,
                        borderRadius: "8px",
                        fontSize: "1rem",
                        fontWeight: 600,
                        background:
                          "linear-gradient(135deg, #00acc1 0%, #00838f 100%)",
                        boxShadow: "0 4px 12px rgba(0, 172, 193, 0.3)",
                        "&:hover": {
                          boxShadow: "0 6px 16px rgba(0, 172, 193, 0.4)",
                          background:
                            "linear-gradient(135deg, #00838f 0%, #006064 100%)",
                        },
                        "&:disabled": {
                          background: "#e0e0e0",
                        },
                      }}
                    >
                      {isTraining ? (
                        <>
                          <CircularProgress
                            size={24}
                            sx={{ mr: 1, color: "inherit" }}
                          />
                          Training...
                        </>
                      ) : (
                        "Start Training"
                      )}
                    </Button>
                  </Box>
                </Box>
              ) : (
                <Box className="no-data">
                  <Typography variant="h6" color="textSecondary" gutterBottom>
                    No training data available
                  </Typography>
                  <Typography
                    variant="body1"
                    color="textSecondary"
                    sx={{ mb: 2 }}
                  >
                    Please upload and annotate images to train your model
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => setActiveTab(0)}
                    className="action-button"
                  >
                    Go to Upload
                  </Button>
                </Box>
              )}
            </Box>
          )}
        </Box>
      </Box>

      <Dialog
        open={previewOpen}
        onClose={closePreview}
        maxWidth="md"
        fullWidth
        sx={{
          "& .MuiDialog-paper": {
            borderRadius: "16px",
            overflow: "hidden",
          },
        }}
      >
        <DialogTitle
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            backgroundColor: "#f8f9fa",
            borderBottom: "1px solid rgba(0, 0, 0, 0.12)",
            padding: "16px 24px",
          }}
        >
          <Box display="flex" alignItems="center">
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {previewImage?.name || "Annotation Preview"}
            </Typography>
            {previewImage?.annotations?.length > 0 && (
              <Chip
                label={`${previewImage.annotations.length} annotations`}
                size="small"
                color="primary"
                sx={{ ml: 2 }}
              />
            )}
          </Box>
          <IconButton onClick={closePreview}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent
          dividers
          sx={{
            backgroundColor: "#f5f5f5",
            position: "relative",
            minHeight: "400px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            padding: 0,
          }}
        >
          {previewImage && (
            <Box
              sx={{
                position: "relative",
                display: "inline-block",
                maxWidth: "100%",
                borderRadius: "8px",
                overflow: "hidden",
                margin: "16px",
              }}
            >
              <img
                src={previewImage.url}
                alt={previewImage.name}
                style={{
                  maxWidth: "100%",
                  maxHeight: "70vh",
                  display: "block",
                  borderRadius: "8px",
                }}
                onLoad={(e) => {
                  const img = e.target;
                  const canvas = canvasRef.current;
                  if (canvas && previewImage?.annotations?.length > 0) {
                    const ctx = canvas.getContext("2d");
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    previewImage.annotations.forEach((box) => {
                      const x = box.x * canvas.width;
                      const y = box.y * canvas.height;
                      const w = box.width * canvas.width;
                      const h = box.height * canvas.height;

                      ctx.strokeStyle = "#FF0000";
                      ctx.lineWidth = 2;
                      ctx.strokeRect(x, y, w, h);
                      ctx.fillStyle = "#FF0000";
                      ctx.font = "12px Arial";
                      ctx.fillText(box.class, x + 5, y + 15);
                    });
                  }
                }}
              />
              <canvas
                ref={canvasRef}
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  pointerEvents: "none",
                  width: "100%",
                  height: "100%",
                }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            startIcon={<Download />}
            onClick={() => downloadImage(previewImage?.url, previewImage?.name)}
            className="action-button"
          >
            Download
          </Button>
          <Button onClick={closePreview} className="action-button">
            Close
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default TrainingModelDashboard;
