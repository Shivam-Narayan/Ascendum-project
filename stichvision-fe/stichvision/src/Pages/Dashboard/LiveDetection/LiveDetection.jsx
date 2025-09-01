import React, { useRef, useState, useEffect } from "react";
import { Button, Box, Typography, Paper } from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import ImageIcon from "@mui/icons-material/Image";
import DefectResults from "./DefectResults";
import LiveDetectionApi from "../../../Services/LiveDetectionApi";
import "./LiveDetection.css";

function LiveDetection({ token }) {
  const [batchId, setBatchId] = useState(null);
  const [streamStarted, setStreamStarted] = useState(false);
  const [videoStream, setVideoStream] = useState(null);
  const [results, setResults] = useState([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);
  const isSendingRef = useRef(false);

  // Set the token in localStorage for the API interceptor
  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    }
  }, [token]);

  // Load results from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("liveDetectionResults");
    if (saved) setResults(JSON.parse(saved));
  }, []);

  // Save results to localStorage
  useEffect(() => {
    if (results.length > 0)
      localStorage.setItem("liveDetectionResults", JSON.stringify(results));
  }, [results]);

  // ---------------- START ----------------
  const handleStart = async () => {
    setResults([]);
    try {
      const newBatchId = await LiveDetectionApi.getLiveBatchId();
      setBatchId(newBatchId);

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } },
      });
      videoRef.current.srcObject = stream;
      setVideoStream(stream);
      setStreamStarted(true);

      intervalRef.current = setInterval(async () => {
        if (!videoRef.current) return;
        if (isSendingRef.current) return;
        isSendingRef.current = true;

        const canvas = canvasRef.current;
        canvas.width = 340;
        canvas.height = 240;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        const base64Image = canvas.toDataURL("image/jpeg", 0.6);

        try {
          const data = await LiveDetectionApi.detectDefectLive(newBatchId, base64Image);
          setResults((prev) => [
            ...prev,
            {
              class_names: data.defects ? data.defects.map((d) => d.class) : [],
              image_url: data.image_url || null,
              annotated_image: null,
              source: "live",
            },
          ]);
        } catch (err) {
          console.error("Frame send failed", err);
        } finally {
          isSendingRef.current = false;
        }
      }, 500);
    } catch (err) {
      console.error(err);
      alert("Failed to start live detection");
      setStreamStarted(false);
    }
  };

  // ---------------- STOP ----------------
  const handleStop = async () => {
    if (videoStream) {
      videoStream.getTracks().forEach((track) => track.stop());
      setVideoStream(null);
    }
    setStreamStarted(false);
    clearInterval(intervalRef.current);

    if (batchId) {
      try {
        const sessionResults = await LiveDetectionApi.stopLiveDetection(batchId);
        setResults(sessionResults);
      } catch (err) {
        console.error("Failed to fetch session results", err);
      }
    }
  };

  // ---------------- CLEAR ----------------
  const handleClearAll = () => {
    setResults([]);
    localStorage.removeItem("liveDetectionResults");
  };

  return (
    <Box className="live-detection-container">
      <Typography variant="h4" className="live-detection-title">
        Live Defect Detection
      </Typography>

      <Box className="live-detection-controls">
        <Button
          variant="contained"
          startIcon={<PlayArrowIcon />}
          onClick={handleStart}
        >
          Start Live Detection
        </Button>
        <Button
          variant="contained"
          color="error"
          startIcon={<StopIcon />}
          onClick={handleStop}
        >
          Stop & Show Results
        </Button>
      </Box>

      <Paper elevation={4} className="batch-id-box">
        <Typography variant="subtitle1">
          Batch ID:&nbsp;<span>{batchId || "Not started"}</span>
        </Typography>
      </Paper>

      <Box className="live-stream">
        <video
          ref={videoRef}
          autoPlay
          muted
          style={{
            width: 400,
            borderRadius: "12px",
            visibility: streamStarted ? "visible" : "hidden",
            position: streamStarted ? "relative" : "absolute",
          }}
        />
        {!streamStarted && (
          <Box
            sx={{
              width: 400,
              height: 300,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "2px dashed #1976d2",
              borderRadius: "12px",
              background: "#f5faff",
              margin: "0 auto",
              visibility: streamStarted ? "hidden" : "visible",
            }}
          >
            <ImageIcon sx={{ fontSize: 64, color: "#b0bec5" }} />
          </Box>
        )}
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </Box>

      {results.length > 0 && (
        <DefectResults results={results} onClearAll={handleClearAll} />
      )}
    </Box>
  );
}

export default LiveDetection;