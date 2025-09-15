import React, { useState, useRef, useCallback } from 'react';
import { Upload, Camera, X, CheckCircle, AlertCircle } from 'lucide-react';
import './ImageUpload.css';

const ImageUpload = ({ 
  onImageSelect, 
  onAnalyze, 
  isAnalyzing, 
  showWebcam = true 
}) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [useWebcam, setUseWebcam] = useState(false);
  const [webcamStream, setWebcamStream] = useState(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (file) => {
    if (file.type.startsWith('image/')) {
      setSelectedImage(file);
      onImageSelect(file);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      setWebcamStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Error accessing webcam:', error);
    }
  };

  const stopWebcam = () => {
    if (webcamStream) {
      webcamStream.getTracks().forEach(track => track.stop());
      setWebcamStream(null);
    }
  };

  const captureImage = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0);
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
            handleFileSelect(file);
            setUseWebcam(false);
            stopWebcam();
          }
        }, 'image/jpeg');
      }
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="image-upload-container space-y-6">
      {!selectedImage && !useWebcam && (
        <>
          <div
            className={`upload-area ${
              dragActive 
                ? 'drag-active' 
                : ''
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="upload-icon" />
            <p className="upload-text">Drag and drop file here</p>
            <p className="upload-subtext">Limit 200MB per file • JPG, JPEG, PNG</p>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn btn-primary"
            >
              Browse files
            </button>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileInput}
              className="hidden-input"
            />
          </div>

          {showWebcam && (
            <div className="webcam-controls">
              <input
                type="checkbox"
                id="useWebcam"
                checked={useWebcam}
                onChange={(e) => {
                  setUseWebcam(e.target.checked);
                  if (e.target.checked) {
                    startWebcam();
                  } else {
                    stopWebcam();
                  }
                }}
                className="checkbox"
              />
              <label htmlFor="useWebcam" className="checkbox-label">
                <Camera size={16} />
                <span>Use webcam</span>
              </label>
            </div>
          )}
        </>
      )}

      {useWebcam && !selectedImage && (
        <div className="webcam-container space-y-4">
          <div className="video-container">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="video-element"
            />
          </div>
          <div className="webcam-button-group">
            <button
              onClick={captureImage}
              className="btn btn-primary btn-icon"
            >
              <Camera size={16} />
              <span>Capture</span>
            </button>
            <button
              onClick={() => {
                setUseWebcam(false);
                stopWebcam();
              }}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {selectedImage && imagePreview && (
        <div className="preview-container space-y-4">
          <div className="preview-card">
            <button
              onClick={removeImage}
              className="remove-button"
            >
              <X size={16} />
            </button>
            <img
              src={imagePreview}
              alt="Selected file preview"
              className="preview-image"
            />
            <div className="preview-info">
              <span className="file-name">{selectedImage.name}</span>
              <div className="ready-indicator">
                <CheckCircle size={16} />
                <span className="ready-text">Ready for analysis</span>
              </div>
            </div>
          </div>

          <button
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="btn btn-primary btn-full-width btn-icon"
          >
            {isAnalyzing ? (
              <>
                <div className="loading-spinner"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <AlertCircle size={16} />
                <span>Analyze Image</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;