import React, { useState } from "react";
import {
  Box,
  Grid,
  Card,
  CardMedia,
  CardActionArea,
  Modal,
  Typography,
  Paper,
  Button,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { saveAs } from "file-saver";
import JSZip from "jszip";
import "./LiveDetection.css";

function DefectResults({ results, onClearAll }) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(null);

  if (!results || results.length === 0) {
    return (
      <Paper elevation={2} className="no-defects">
        No defects detected in this session.
      </Paper>
    );
  }

  // ---------------- Download All as ZIP ----------------
  const handleDownloadAll = async () => {
    if (!results.length) return;
    const zip = new JSZip();
    for (const item of results) {
      try {
        // Choose annotated_image if exists, else image_url
        let blob;
        if (item.annotated_image) {
          const res = await fetch(item.annotated_image);
          blob = await res.blob();
        } else if (item.image_url) {
          const res = await fetch(item.image_url);
          blob = await res.blob();
        }
        const annotation = `Classes: ${item.class_names.join(", ")}\nSource: ${item.source}`;
        zip.file(`${item.class_names.join("_")}_${item.source}.jpg`, blob);
        zip.file(`${item.class_names.join("_")}_${item.source}.txt`, annotation);
      } catch (e) {
        console.warn("Failed to add file to zip", e);
      }
    }
    const content = await zip.generateAsync({ type: "blob" });
    saveAs(content, "defect_images.zip");
  };

  const handleOpen = (item) => {
    setSelected(item);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelected(null);
  };

  // ---------------- Download Single Image ----------------
  const handleDownload = async (item) => {
    try {
      let blob;
      if (item.annotated_image) {
        const res = await fetch(item.annotated_image);
        blob = await res.blob();
      } else if (item.image_url) {
        const res = await fetch(item.image_url);
        blob = await res.blob();
      }
      saveAs(blob, `${item.class_names.join("_")}_${item.source}.jpg`);
      const annotation = `Classes: ${item.class_names.join(", ")}\nSource: ${item.source}`;
      const annotationBlob = new Blob([annotation], { type: "text/plain" });
      saveAs(annotationBlob, `${item.class_names.join("_")}_${item.source}.txt`);
    } catch (e) {
      alert("Failed to download image.");
    }
  };

  return (
    <Box className="defect-results">
      <Typography variant="h5" className="defect-results-title">
        Defected Images
      </Typography>

      {/* Action Buttons */}
      <Box sx={{ display: "flex", gap: 2, mb: 2, justifyContent: "flex-end" }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleDownloadAll}
          startIcon={<DownloadIcon />}
        >
          Download All
        </Button>
        <Button
          variant="contained"
          color="error"
          onClick={onClearAll}
        >
          Clear All
        </Button>
      </Box>

      <Box className="defect-results-container">
        <Grid container spacing={2} justifyContent="center">
          {results.map((item, idx) => (
            <Grid item xs={12} sm={6} md={3} lg={3} xl={3} key={idx} className="defect-grid-item">
              <Card className="defect-card">
                <CardActionArea onClick={() => handleOpen(item)}>
                  <CardMedia
                    component="img"
                    image={item.annotated_image || item.image_url}
                    alt="Defect"
                    className="defect-img"
                  />
                </CardActionArea>
                {/* Download Button */}
                <Box sx={{ display: "flex", justifyContent: "center", p: 1 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownload(item)}
                  >
                    Download
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Modal open={open} onClose={handleClose}>
        <Box className="defect-modal">
          {selected && (
            <>
              <Box className="defect-modal-img-container">
                <img
                  src={selected.annotated_image || selected.image_url}
                  alt="Defected Preview"
                  className="defect-modal-img"
                />
              </Box>
              <Typography variant="h6" className="defect-modal-title">
                Defect Details
              </Typography>
              <Typography variant="subtitle1" className="defect-modal-label">
                Classes:
              </Typography>
              <Typography mb={1} className="defect-modal-text">
                {selected.class_names.join(", ")}
              </Typography>
              <Typography variant="subtitle1" className="defect-modal-label">
                Source:
              </Typography>
              <Typography className="defect-modal-text">
                {selected.source}
              </Typography>
            </>
          )}
        </Box>
      </Modal>
    </Box>
  );
}

export default DefectResults;
