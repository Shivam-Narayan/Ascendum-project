import React, { useState, useRef, useCallback } from 'react';
import { Upload, Camera, X, CheckCircle, AlertCircle } from 'lucide-react';

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
    <div className="space-y-6">
      {!selectedImage && !useWebcam && (
        <>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive 
                ? 'border-green-500 bg-green-50' 
                : 'border-gray-300 hover:border-green-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">Drag and drop file here</p>
            <p className="text-sm text-gray-400 mb-4">Limit 200MB per file • JPG, JPEG, PNG</p>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Browse files
            </button>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileInput}
              className="hidden"
            />
          </div>

          {showWebcam && (
            <div className="flex items-center space-x-3">
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
                className="rounded border-gray-300 text-green-600 focus:ring-green-500"
              />
              <label htmlFor="useWebcam" className="text-sm text-gray-700 cursor-pointer flex items-center space-x-2">
                <Camera size={16} />
                <span>Use webcam</span>
              </label>
            </div>
          )}
        </>
      )}

      {useWebcam && !selectedImage && (
        <div className="space-y-4">
          <div className="bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-64 object-cover"
            />
          </div>
          <div className="flex justify-center space-x-4">
            <button
              onClick={captureImage}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
            >
              <Camera size={16} />
              <span>Capture</span>
            </button>
            <button
              onClick={() => {
                setUseWebcam(false);
                stopWebcam();
              }}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {selectedImage && imagePreview && (
        <div className="space-y-4">
          <div className="relative bg-white rounded-lg border border-gray-200 p-4">
            <button
              onClick={removeImage}
              className="absolute top-2 right-2 p-1 bg-red-100 text-red-600 rounded-full hover:bg-red-200 transition-colors"
            >
              <X size={16} />
            </button>
            <img
              src={imagePreview}
              alt="Selected file preview"
              className="w-full h-64 object-cover rounded-lg"
            />
            <div className="mt-3 flex items-center justify-between">
              <span className="text-sm text-gray-600">{selectedImage.name}</span>
              <div className="flex items-center space-x-2 text-green-600">
                <CheckCircle size={16} />
                <span className="text-sm">Ready for analysis</span>
              </div>
            </div>
          </div>

          <button
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
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