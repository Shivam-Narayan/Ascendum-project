import React, { useState, useRef, useEffect } from 'react';
import generateThumbnails from '../../services/GenerateThumbnailApi';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import DownloadIcon from '@mui/icons-material/Download';
import LogoutIcon from '@mui/icons-material/Logout';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import generateThumbnailsFromFile from '../../services/generateapi';
import logoutUser from '../../services/logoutapi';
import { 
  Film, 
  Cog, 
  Eye, 
  Cloud, 
  Smile, 
  BarChart2,
  Loader2
} from 'lucide-react';
import './HomeScreen.css';

const Home = () => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [faceConfidence, setFaceConfidence] = useState(0);
  const [faceCoverage, setFaceCoverage] = useState(0);
  const [selectedEmotions, setSelectedEmotions] = useState([]);
  const [showEmotionDropdown, setShowEmotionDropdown] = useState(false);
  const [thumbnails, setThumbnails] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [videoInfo, setVideoInfo] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [downloadedOriginals, setDownloadedOriginals] = useState([]);
  const [downloadedEnhanced, setDownloadedEnhanced] = useState([]);
  const [showDownloadsModal, setShowDownloadsModal] = useState(false);
  const [activeDownloadsTab, setActiveDownloadsTab] = useState('originals');
  const [thumbnailCount, setThumbnailCount] = useState(1);
  const [thumbnailInput, setThumbnailInput] = useState("1");
  const [selectedThumbnails, setSelectedThumbnails] = useState([]);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [showDownloadAllModal, setShowDownloadAllModal] = useState(false);
  const [downloadAllType, setDownloadAllType] = useState('original');
  const [thumbnailError,] = useState('');
  const [generationStats, setGenerationStats] = useState(null);
  const [frameInterval, setFrameInterval] = useState(2); // Default value is 2
  const [, setGenerationProgress] = useState({
    totalFrames: 0,
    processedFrames: 0,
    facesDetected: 0,
    blurryFrames: 0,
    matchingEmotions: 0
  });
  
  const emotions = ['Happy', 'Surprised', 'Angry', 'Sad', 'Neutral'];
  const dropdownRef = useRef(null);
  const faceConfidenceProgressRef = useRef(null);
  const faceCoverageProgressRef = useRef(null);

  const fileInputRef = useRef(null);

  // Load saved data on component mount
  useEffect(() => {
    const userEmail = localStorage.getItem('userEmail');
    if (userEmail) {
      const savedOriginals = JSON.parse(localStorage.getItem(`downloadedOriginals_${userEmail}`)) || [];
      const savedEnhanced = JSON.parse(localStorage.getItem(`downloadedEnhanced_${userEmail}`)) || [];
      const savedTheme = JSON.parse(localStorage.getItem(`userTheme_${userEmail}`));
      const savedThumbnails = JSON.parse(localStorage.getItem(`generatedThumbnails_${userEmail}`));
      
      setIsDarkMode(savedTheme || false);
      setDownloadedOriginals(savedOriginals);
      setDownloadedEnhanced(savedEnhanced);

      if (savedThumbnails) {
        setThumbnails(savedThumbnails.thumbnails);
        setVideoInfo(savedThumbnails.videoInfo);
        setGenerationStats(savedThumbnails.generationStats);
      }

      if (savedTheme) {
        document.body.classList.add('dark-theme');
      } else {
        document.body.classList.remove('dark-theme');
      }
    }
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowEmotionDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (faceConfidenceProgressRef.current) {
      faceConfidenceProgressRef.current.style.width = `${faceConfidence}%`;
    }
  }, [faceConfidence]);

  useEffect(() => {
    if (faceCoverageProgressRef.current) {
      faceCoverageProgressRef.current.style.width = `${faceCoverage}%`;
    }
  }, [faceCoverage]);

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }, [isDarkMode]);

  const [simulatedProgress, setSimulatedProgress] = useState({
    totalFrames: 0,
    processedFrames: 0,
    facesDetected: 0,
    blurryFrames: 0,
    matchingEmotions: 0
  });

  // Add this new function to handle file selection
  const handleFileSelect = () => {
    fileInputRef.current.value = null; // Reset file input so same file can be selected again
    fileInputRef.current.click();
  };
  
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setYoutubeUrl(file.name);
    }
  };

  const [selectedFile, setSelectedFile] = useState(null);

  const handleLogout = () => {
    setShowLogoutConfirm(true);
  };

  const confirmLogout = async () => {
    const token = localStorage.getItem('token');
    console.log('Token being sent:', token); // Debug log
    
    if (!token) {
      setError('No active session found');
      return;
    }
  
    try {
      const response = await logoutUser(token);
      console.log('Logout response:', response); // Debug log
      
      // Clear local storage and redirect to login
      localStorage.clear();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      setError(error.message || 'Failed to log out');
    }
  };

  const toggleTheme = () => {
    const userEmail = localStorage.getItem('userEmail');
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    
    if (userEmail) {
      localStorage.setItem(`userTheme_${userEmail}`, JSON.stringify(newTheme));
    }
    
    if (newTheme) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  };

  const handleThumbnailSelect = (thumbnailId) => {
    setSelectedThumbnails(prev => 
      prev.includes(thumbnailId)
        ? prev.filter(id => id !== thumbnailId)
        : [...prev, thumbnailId]
    );
  };

  const handleEmotionChange = (emotion) => {
    setSelectedEmotions(prev => 
      prev.includes(emotion)
        ? prev.filter(e => e !== emotion)
        : [...prev, emotion]
    );
  };

  const handleAIEdit = () => {
    if (selectedThumbnails.length === 0) {
      setError('Please select at least one thumbnail to edit');
      return;
    }
    
    const selectedThumbnailData = thumbnails.filter(thumb => 
      selectedThumbnails.includes(thumb.id)
    );
    
    localStorage.setItem('aiEditThumbnails', JSON.stringify({
      thumbnails: selectedThumbnailData,
      videoInfo
    }));
    
    window.location.href = '/AiEdit';
  };

  const clearGeneratedThumbnails = () => {
    const userEmail = localStorage.getItem('userEmail');
    setThumbnails([]);
    setVideoInfo(null);
    setGenerationStats(null);
    setSelectedThumbnails([]);
    if (userEmail) {
      localStorage.removeItem(`generatedThumbnails_${userEmail}`);
    }
  };

  const handleDownloadAll = async () => {
    if (thumbnails.length === 0) return;
  
    try {
      const userEmail = localStorage.getItem('userEmail');
      if (!userEmail) throw new Error("User not logged in");
  
      const JSZip = await import('jszip');
      const zip = new JSZip.default();
      const folder = zip.folder("thumbnails");
  
      let downloadCount = 0;
      for (const thumbnail of thumbnails) {
        const imageUrl = downloadAllType === 'original' 
          ? thumbnail.imageUrl 
          : thumbnail.enhancedImageUrl || thumbnail.imageUrl;
        
        if (!imageUrl) continue;
  
        try {
          const response = await fetch(imageUrl);
          const blob = await response.blob();
          const filename = `thumbnail_${thumbnail.timestamp}.jpg`;
          folder.file(filename, blob);
          downloadCount++;
        } catch (err) {
          console.error(`Failed to download ${imageUrl}:`, err);
        }
      }
  
      if (downloadCount === 0) {
        setError("No thumbnails available to download");
        return;
      }
  
      const content = await zip.generateAsync({ type: "blob" });
      const url = URL.createObjectURL(content);
      const link = document.createElement('a');
      link.href = url;
      link.download = `thumbnails_${new Date().getTime()}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  
      const downloadInfo = {
        id: Date.now(),
        type: downloadAllType,
        count: downloadCount,
        downloadedAt: new Date().toISOString(),
        videoTitle: videoInfo?.title || 'Unknown Video'
      };
  
      if (downloadAllType === 'original') {
        const updatedOriginals = [downloadInfo, ...downloadedOriginals];
        setDownloadedOriginals(updatedOriginals);
        localStorage.setItem(`downloadedOriginals_${userEmail}`, JSON.stringify(updatedOriginals));
      } else {
        const updatedEnhanced = [downloadInfo, ...downloadedEnhanced];
        setDownloadedEnhanced(updatedEnhanced);
        localStorage.setItem(`downloadedEnhanced_${userEmail}`, JSON.stringify(updatedEnhanced));
      }
  
    } catch (err) {
      console.error('Download all failed:', err);
      setError("Failed to download all thumbnails");
    }
  };

  const getBackendFaceCoverage = (value) => {
    if (value <= 20) return 1;
    if (value <= 40) return 2;
    if (value <= 60) return 3;
    if (value <= 80) return 4;
    return 5;
  };

  // const handleGenerate = async () => {
  //   if (!youtubeUrl && !selectedFile) {
  //     setError('Please enter a YouTube URL or select a video file');
  //     return;
  //   }
  
  //   setError(null);
  //   setIsGenerating(true);
  //   setThumbnails([]);
  //   setVideoInfo(null);
  //   setGenerationStats(null);
  //   setSelectedThumbnails([]);
  //   setGenerationProgress({
  //     totalFrames: 0,
  //     processedFrames: 0,
  //     facesDetected: 0,
  //     blurryFrames: 0,
  //     matchingEmotions: 0
  //   });
  
  //   try {
  //     let requestData = {
  //       face_threshold: faceConfidence / 100,
  //       face_coverage: getBackendFaceCoverage(faceCoverage),
  //       num_thumbnails: thumbnailCount,
  //       include_emotions: selectedEmotions.length > 0,
  //       selected_emotions: selectedEmotions.map((e) => e.toLowerCase()),
  //       frame_interval: frameInterval, // Use the dynamic value here
  //       max_workers: 4,
  //       blur_threshold: 100,
  //       enable_stabilization: true,
  //       enable_enhancement: true,
  //       enable_autosave: false,
  //       save_location: "thumbnails",
  //       save_format: "jpg",
  //     };
  
  //     // if (selectedFile) {
  //     //   const formData = new FormData();
  //     //   formData.append('video_file', selectedFile);
  //     //   Object.keys(requestData).forEach(key => {
  //     //     formData.append(key, 
  //     //       typeof requestData[key] === 'object' 
  //     //         ? JSON.stringify(requestData[key]) 
  //     //         : requestData[key]
  //     //     );
  //     //   });

  //     if (selectedFile) {
  //       const formData = new FormData();
  //       formData.append('video_file', selectedFile);

  //       // Append all other fields except selected_emotions
  //       Object.keys(requestData).forEach(key => {
  //         if (key !== 'selected_emotions') {
  //           formData.append(key, 
  //             typeof requestData[key] === 'object' 
  //               ? JSON.stringify(requestData[key]) 
  //               : requestData[key]
  //           );
  //         }
  //       });

  //       // Append each emotion separately
  //       requestData.selected_emotions.forEach(emotion => {
  //         formData.append('selected_emotions', emotion);
  //       });

  
  //       const { thumbnails: generatedThumbnails, videoInfo: generatedVideoInfo, stats } = 
  //         await generateThumbnailsFromFile(formData);
  
  //       setThumbnails(generatedThumbnails.slice(0, thumbnailCount));
  //       setVideoInfo(generatedVideoInfo);
  //       setGenerationStats(stats);
  
  //       // Save to localStorage
  //       const userEmail = localStorage.getItem('userEmail');
  //       if (userEmail) {
  //         localStorage.setItem(`generatedThumbnails_${userEmail}`, JSON.stringify({
  //           thumbnails: generatedThumbnails,
  //           videoInfo: generatedVideoInfo,
  //           generationStats: stats
  //         }));
  //       }
  //     } else {
  //       requestData.youtube_url = youtubeUrl;
  
  //       const { thumbnails: generatedThumbnails, videoInfo: generatedVideoInfo, stats } = 
  //         await generateThumbnails(requestData);
  
  //       setThumbnails(generatedThumbnails.slice(0, thumbnailCount));
  //       setVideoInfo(generatedVideoInfo);
  //       setGenerationStats(stats);
  
  //       // Save to localStorage
  //       const userEmail = localStorage.getItem('userEmail');
  //       if (userEmail) {
  //         localStorage.setItem(`generatedThumbnails_${userEmail}`, JSON.stringify({
  //           thumbnails: generatedThumbnails,
  //           videoInfo: generatedVideoInfo,
  //           generationStats: stats
  //         }));
  //       }
  //     }
  //   } catch (err) {
  //     setError("An error occurred while generating thumbnails");
  //     console.error("Generation error:", err);
  //   } finally {
  //     setIsGenerating(false);
  //   }
  // };

  const handleGenerate = async () => {
    if (!youtubeUrl && !selectedFile) {
      setError('Please enter a YouTube URL or select a video file');
      return;
    }

    setError(null);
    setIsGenerating(true);
    setThumbnails([]);
    setVideoInfo(null);
    setGenerationStats(null);
    setSelectedThumbnails([]);
    setGenerationProgress({
      totalFrames: 0,
      processedFrames: 0,
      facesDetected: 0,
      blurryFrames: 0,
      matchingEmotions: 0
    });

    try {
      let requestData = {
        face_threshold: faceConfidence / 100,
        face_coverage: getBackendFaceCoverage(faceCoverage),
        num_thumbnails: thumbnailCount,
        include_emotions: selectedEmotions.length > 0,
        selected_emotions: selectedEmotions.map((e) => e.toLowerCase()),
        frame_interval: frameInterval,
        max_workers: 4,
        blur_threshold: 100,
        enable_stabilization: true,
        enable_enhancement: true,
        enable_autosave: false,
        save_location: "thumbnails",
        save_format: "jpg",
      };

      // Always use FormData
      const formData = new FormData();

      if (selectedFile) {
        formData.append('video_file', selectedFile);
      } else {
        formData.append('youtube_url', youtubeUrl);
      }

      // Append all other fields except selected_emotions
      Object.keys(requestData).forEach(key => {
        if (key !== 'selected_emotions') {
          formData.append(
            key,
            typeof requestData[key] === 'object'
              ? JSON.stringify(requestData[key])
              : requestData[key]
          );
        }
      });

      // Append each emotion separately
      requestData.selected_emotions.forEach(emotion => {
        formData.append('selected_emotions', emotion);
      });

      // Debug: log FormData
      for (let pair of formData.entries()) {
        console.log(pair[0] + ':', pair[1]);
      }

      let response;
      if (selectedFile) {
        response = await generateThumbnailsFromFile(formData);
      } else {
        response = await generateThumbnailsFromFile(formData); // Use the same API for both
      }

      const { thumbnails: generatedThumbnails, videoInfo: generatedVideoInfo, stats } = response;

      setThumbnails(generatedThumbnails.slice(0, thumbnailCount));
      setVideoInfo(generatedVideoInfo);
      setGenerationStats(stats);

      // Save to localStorage
      const userEmail = localStorage.getItem('userEmail');
      if (userEmail) {
        localStorage.setItem(`generatedThumbnails_${userEmail}`, JSON.stringify({
          thumbnails: generatedThumbnails,
          videoInfo: generatedVideoInfo,
          generationStats: stats
        }));
      }
    } catch (err) {
      setError("An error occurred while generating thumbnails");
      console.error("Generation error:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  const renderRealTimeAnalytics = () => {
    // Calculate percentages for progress bars
    const isProcessing = true;
  
    const processingPercent = simulatedProgress.totalFrames > 0
      ? Math.round((simulatedProgress.processedFrames / simulatedProgress.totalFrames) * 100)
      : 0;
  
    const faceDetectionPercent = simulatedProgress.processedFrames > 0
      ? Math.round((simulatedProgress.facesDetected / simulatedProgress.processedFrames) * 100)
      : 0;
  
    return (
      <div className="analytics-container w-full max-w-6xl">
        {/* Header */}
        <div className="analytics-header">
          <BarChart2 className="header-icon" />
          <h3 className="analytics-title">
            Video Analysis
            {isProcessing && (
              <span className="processing-indicator">
                <Loader2 className="spinner-icon" />
                in progress
              </span>
            )}
          </h3>
        </div>
  
        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="icon-wrapper bg-blue">
              <Film className="icon text-blue" />
            </div>
            <div className="stat-value">{simulatedProgress.totalFrames}</div>
            <div className="stat-label">Total Frames</div>
          </div>
  
          <div className="stat-card">
            <div className="icon-wrapper bg-green">
              <Cog className="icon text-green" />
            </div>
            <div className="stat-value">{simulatedProgress.processedFrames}</div>
            <div className="stat-label">Processed</div>
          </div>
  
          <div className="stat-card">
            <div className="icon-wrapper bg-purple">
              <Eye className="icon text-purple" />
            </div>
            <div className="stat-value">{simulatedProgress.facesDetected}</div>
            <div className="stat-label">Thumbnails Generated</div>
          </div>
  
          <div className="stat-card">
            <div className="icon-wrapper bg-gray">
              <Cloud className="icon text-gray" />
            </div>
            <div className="stat-value">{simulatedProgress.blurryFrames}</div>
            <div className="stat-label">Blurry</div>
          </div>
  
          {selectedEmotions.length > 0 && (
            <div className="stat-card">
              <div className="icon-wrapper bg-yellow">
                <Smile className="icon text-yellow" />
              </div>
              <div className="stat-value">
                {simulatedProgress.matchingEmotions}
                <div className="emotion-list" style={{ fontSize: '0.8em', marginTop: 4 }}>
                  {selectedEmotions.join(', ')}
                </div>
              </div>
              <div className="stat-label">Matching</div>
            </div>
          )}
        </div>
  
        {/* Progress Bars */}
        <div className="progress-section">
          <div className="progress-item">
            <div className="progress-header">
              <span className="progress-label">Processing Progress</span>
              <span className="progress-percent-blue">{processingPercent}%</span>
            </div>
            <div className="progress-bar-container">
              <div
                className="progress-bar-blue"
                style={{ width: `${processingPercent}%` }}
              ></div>
            </div>
          </div>
  
          <div className="progress-item">
            <div className="progress-header">
              <span className="progress-label">Face Detection Rate</span>
              <span className="progress-percent-purple">{faceDetectionPercent}%</span>
            </div>
            <div className="progress-bar-container">
              <div
                className="progress-bar-purple"
                style={{ width: `${faceDetectionPercent}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    );
  };
  

  useEffect(() => {
    let interval;
  
    if (isGenerating) {
      // Reset progress when generation starts
      setSimulatedProgress({
        totalFrames: Math.floor(Math.random() * 200) + 100, // Random total frames (100-300)
        processedFrames: 0,
        facesDetected: 0,
        blurryFrames: 0,
        matchingEmotions: 0,
      });
  
      interval = setInterval(() => {
        setSimulatedProgress((prev) => {
          const isComplete = prev.processedFrames >= prev.totalFrames;
          if (isComplete) {
            clearInterval(interval);
            return {
              ...prev,
              processedFrames: prev.totalFrames,
              facesDetected: Math.min(thumbnailCount, prev.totalFrames), // Ensure facesDetected matches thumbnailCount
              blurryFrames: Math.floor(thumbnailCount * 0.2), // 20% of thumbnails are blurry
              matchingEmotions: selectedEmotions.length
                ? Math.floor(thumbnailCount * 0.6) // 60% of thumbnails match emotions
                : 0,
            };
          }
  
          // Simulate non-linear progress
          const progressFactor = prev.processedFrames / prev.totalFrames;
          const increment = Math.floor(
            (Math.random() * 10 + 5) * (1 - progressFactor) + 5
          ); // Slower as progressFactor approaches 1
  
          // Random fluctuations
          const fluctuation = Math.random() < 0.1 ? -1 : 0; // Occasionally decrease progress
  
          // Update processed frames
          const newProcessedFrames = Math.min(
            prev.processedFrames + increment + fluctuation,
            prev.totalFrames
          );
  
          // Simulate face detection only if faceConfidence or faceCoverage is greater than 0
          let newFacesDetected = prev.facesDetected;
          if (faceConfidence > 0 || faceCoverage > 0) {
            const faceDetectionRate = (faceConfidence * faceCoverage) / 100; // Scale detection rate
            const maxFaces = Math.min(thumbnailCount, prev.totalFrames); // Cap at thumbnailCount
            newFacesDetected = Math.min(
              prev.facesDetected + Math.floor(faceDetectionRate * increment),
              maxFaces
            );
          }
  
          const newBlurryFrames = Math.min(
            prev.blurryFrames + Math.floor(Math.random() * 1),
            Math.floor(thumbnailCount * 0.2)
          );
  
          const newMatchingEmotions = selectedEmotions.length
            ? Math.min(
                prev.matchingEmotions + Math.floor(Math.random() * 2),
                Math.floor(thumbnailCount * 0.6)
              )
            : 0;
  
          return {
            ...prev,
            processedFrames: newProcessedFrames,
            facesDetected: newFacesDetected,
            blurryFrames: newBlurryFrames,
            matchingEmotions: newMatchingEmotions,
          };
        });
      }, 500); // Update every 500ms
    }
  
    return () => clearInterval(interval);
  }, [isGenerating, selectedEmotions.length, thumbnailCount, faceConfidence, faceCoverage]);

  const renderAnalyticsStats = () => {
    if (!generationStats) return null;

    return (
      <div className="analytics-stats-container">
        <h3 className="analytics-title">Video Analysis Summary</h3>
        
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{generationStats.total_frames}</div>
            <div className="stat-label">Total Frames</div>
          </div>
          
          <div className="stat-item">
            <div className="stat-value">{generationStats.frames_with_faces}</div>
            <div className="stat-label">Thumbnails Generated</div>
          </div>
          
          <div className="stat-item">
            <div className="stat-value">{generationStats.blurry_frames}</div>
            <div className="stat-label">Blurry Frames</div>
          </div>
          
          {selectedEmotions.length > 0 && (
            <div className="stat-item">
              <div className="stat-value">{generationStats.frames_with_matching_emotions}</div>
              <div className="stat-label">Matching Emotions</div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return '0:00';
    const time = String(timeStr); 
    if (time.includes(':')) return time;
    const seconds = parseInt(time, 10); 
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const downloadImage = async (imageUrl, isEnhanced = false) => {
    try {
      const userEmail = localStorage.getItem('userEmail');
      if (!userEmail) throw new Error("User not logged in");
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const timestamp = new Date().getTime();
      const videoTitle = videoInfo ? videoInfo.title.replace(/[^a-z0-9]/gi, '_').toLowerCase() : 'thumbnail';
      const filename = `${videoTitle}_${timestamp}.jpg`;
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      const downloadInfo = {
        id: Date.now(),
        url: imageUrl,
        filename,
        videoTitle: videoInfo?.title || 'Unknown Video',
        downloadedAt: new Date().toISOString(),
        isEnhanced,
      };
      
      if (isEnhanced) {
        const updatedEnhanced = [downloadInfo, ...downloadedEnhanced];
        setDownloadedEnhanced(updatedEnhanced);
        localStorage.setItem(`downloadedEnhanced_${userEmail}`, JSON.stringify(updatedEnhanced));
      } else {
        const updatedOriginals = [downloadInfo, ...downloadedOriginals];
        setDownloadedOriginals(updatedOriginals);
        localStorage.setItem(`downloadedOriginals_${userEmail}`, JSON.stringify(updatedOriginals));
      }
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const clearDownloads = (type) => {
    const userEmail = localStorage.getItem('userEmail');
    if (!userEmail) return;
  
    if (type === 'original') {
      setDownloadedOriginals([]);
      localStorage.removeItem(`downloadedOriginals_${userEmail}`);
    } else {
      setDownloadedEnhanced([]);
      localStorage.removeItem(`downloadedEnhanced_${userEmail}`);
    }
  };

  const renderDownloadsPreview = () => {
    const totalDownloads = downloadedOriginals.length + downloadedEnhanced.length;
    return (
      <div className="downloads-preview">
        <div className="downloads-count" onClick={() => setShowDownloadsModal(true)}>
          <span>{totalDownloads} items downloaded</span>
          <span className="view-all">View All →</span>
        </div>
        <div className="downloads-preview-items">
          <div className="preview-item">
            <span className="preview-label">Originals:</span>
            <span className="preview-count">{downloadedOriginals.length}</span>
          </div>
          <div className="preview-item">
            <span className="preview-label">Enhanced:</span>
            <span className="preview-count">{downloadedEnhanced.length}</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="home-container">
      <div className="sidebar">
        <div className="sidebar-content">
          <div className="sidebar-header">
            <h1 className="sidebar-title">Thumbnail Generator</h1>
            <div className="header-controls">
              <button 
                className="theme-toggle"
                onClick={toggleTheme}
                title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
              >
                {isDarkMode ? '☀️' : '🌙'}
              </button>
              <button 
                className="logout-button"
                onClick={handleLogout}
                title="Logout"
              >
                <LogoutIcon fontSize="small" />
              </button>
            </div>
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label>YouTube URL or Local Video</label>
            <div className="url-input-container">
              <input
                type="text"
                value={youtubeUrl}
                onChange={(e) => {
                  setYoutubeUrl(e.target.value);
                  if (selectedFile) {
                    setSelectedFile(null); // Clear selected file if URL is manually changed
                  }
                }}
                placeholder="Enter YouTube URL or select a video file"
                className="dark-theme-input"
              />
              <button 
                className="file-input-button"
                onClick={handleFileSelect}
                title="Select video file"
              >
                <AttachFileIcon fontSize="small" />
              </button>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="video/*"
                style={{ display: 'none' }}
              />
            </div>
            {selectedFile && (
              <div className="selected-file-info">
                <span className="file-name">{selectedFile.name}</span>
                <span className="file-size">({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)</span>
                <button 
                  className="clear-file-button"
                  onClick={() => {
                    setSelectedFile(null);
                    setYoutubeUrl('');
                    fileInputRef.current.value = null;
                  }}
                >
                  ×
                </button>
              </div>
            )}
          </div>

          <div className="settings-section">
            <h3>Configure Settings</h3>
            
            <div className="form-group">
              <label>Number of Thumbnails to Generate</label>
              <input
                type="number"
                min="1"
                max="100"
                step="1"
                value={thumbnailInput}
                onChange={(e) => {
                  setThumbnailInput(e.target.value); // Just update the text box
                }}
                onBlur={(e) => {
                  const parsed = parseInt(thumbnailInput, 10);
                  if (!isNaN(parsed)) {
                    const clamped = Math.max(1, Math.min(100, parsed));
                    setThumbnailCount(clamped);               // Save valid number
                    setThumbnailInput(clamped.toString());    // Reflect in input
                  } else {
                    setThumbnailCount(1);
                    setThumbnailInput("1");
                  }
                }}
                className={`dark-theme-input no-spinner ${thumbnailError ? 'input-error' : ''}`}
              />
              {thumbnailError && <div className="error-message">{thumbnailError}</div>}
            </div>
            
            <div className="slider-group">
              <label>Face Confidence: {faceConfidence}%</label>
              <span className="slider-value">{faceConfidence}%</span>
              <div className="slider-wrapper">
                <div className="slider-track">
                  <div className="slider-progress" ref={faceConfidenceProgressRef}></div>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={faceConfidence}
                  onChange={(e) => setFaceConfidence(parseInt(e.target.value))}
                  className="ios-slider"
                />
              </div>
            </div>

            <div className="slider-group">
              <label>Face Coverage: Level {getBackendFaceCoverage(faceCoverage)} (1-5)</label>
              <span className="slider-value">{faceCoverage}%</span>
              <div className="slider-wrapper">
                <div className="slider-track">
                  <div className="slider-progress" ref={faceCoverageProgressRef}></div>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="20"
                  value={faceCoverage}
                  onChange={(e) => setFaceCoverage(parseInt(e.target.value))}
                  className="ios-slider"
                />
              </div>
            </div>

            <div className="slider-group">
              <label>Frame Interval: {frameInterval}</label>
              <span className="slider-value">{frameInterval}</span>
              <div className="slider-wrapper">
                <div className="slider-track">
                  <div className="slider-progress" style={{ width: `${(frameInterval - 1) * 11.11}%` }}></div>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={frameInterval}
                  onChange={(e) => setFrameInterval(parseInt(e.target.value))}
                  className="ios-slider"
                />
              </div>
            </div>

            <div className="form-group emotion-filter-group" ref={dropdownRef}>
              <label>Filter by Emotion</label>
              <div 
                className="ios-dropdown-select"
                onClick={() => setShowEmotionDropdown(!showEmotionDropdown)}
              >
                {selectedEmotions.length > 0 
                  ? selectedEmotions.join(', ') 
                  : 'Select emotions...'}
                <span className="dropdown-arrow">▼</span>
              </div>
              
              {showEmotionDropdown && (
                <div className="ios-dropdown-options">
                  {emotions.map(emotion => (
                    <label key={emotion} className="ios-dropdown-option">
                      <input
                        type="checkbox"
                        checked={selectedEmotions.includes(emotion)}
                        onChange={() => handleEmotionChange(emotion)}
                        className="ios-checkbox"
                      />
                      <span className="ios-checkbox-custom"></span>
                      {emotion}
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="downloads-preview-section">
            {renderDownloadsPreview()}
          </div>

          <button 
            className="generate-button"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <span className="spinner"></span>
                Generating...
              </>
            ) : 'Generate Thumbnails'}
          </button>

          {thumbnails.length > 0 && (
            <button 
              className="clear-thumbnails-button"
              onClick={clearGeneratedThumbnails}
            >
              Clear Thumbnails
            </button>
          )}
        </div>
      </div>

      <div className="main-content">
        <div className="content-header-container">
          <div className="content-header">
            <h2>Generated Thumbnails</h2>
            {videoInfo && (
              <div className="video-info">
                <span>{videoInfo.title}</span>
              </div>
            )}
            <div className="header-actions">
              <button 
                className="download-all-button"
                onClick={() => setShowDownloadAllModal(true)}
                disabled={thumbnails.length === 0}
              >
                <DownloadIcon fontSize="small" sx={{ mr: 0.5 }} />
                Download All
              </button>
              <button 
                className={`ai-edit-button ${selectedThumbnails.length === 0 ? 'disabled' : ''}`} 
                onClick={handleAIEdit}
                disabled={selectedThumbnails.length === 0}
              >
                ✨AI Edit ({selectedThumbnails.length})
              </button>
            </div>
          </div>
        </div>

        <div className="thumbnails-container">
          {isGenerating ? (
            <div className="loading-state">
              {renderRealTimeAnalytics()}
            </div>
          ) : thumbnails.length > 0 ? (
            <div>
              {renderAnalyticsStats()}
              <div className="thumbnails-grid">
                {thumbnails.map((thumbnail) => (
                  <div key={thumbnail.id} className="thumbnail-card">
                    <div className="thumbnail-checkbox-container">
                      <input
                        type="checkbox"
                        id={`thumbnail-checkbox-${thumbnail.id}`}
                        checked={selectedThumbnails.includes(thumbnail.id)}
                        onChange={() => handleThumbnailSelect(thumbnail.id)}
                        className="ios-checkbox"
                      />
                      <label htmlFor={`thumbnail-checkbox-${thumbnail.id}`} className="ios-checkbox-label"></label>
                    </div>
                    
                    <div className="thumbnail-image-container">
                      <img 
                        src={thumbnail.imageUrl} 
                        alt={`Thumbnail at ${thumbnail.timestamp}`} 
                        className="thumbnail-image"
                      />
                      <div className="thumbnail-timestamp">
                        {formatTime(thumbnail.timestamp || 0)}
                      </div>
                    </div>
                    
                    <div className="thumbnail-details">
                      <div className="thumbnail-emotion">
                        <span className={`emotion-badge ${thumbnail.emotion.toLowerCase()}`}>
                          {thumbnail.emotion}
                        </span>
                        <span className="face-coverage">{thumbnail.faceCoverage}% face</span>
                      </div>
                    </div>
                    
                    <div className="thumbnail-actions">
                      <button 
                        className="download-button"
                        onClick={() => downloadImage(thumbnail.imageUrl, false)}
                      >
                        <DownloadIcon fontSize="small" sx={{ mr: 0.5 }} />
                        Download
                      </button>
                      <button
                        className="edit-button"
                        onClick={() => setPreviewImage(thumbnail.enhancedImageUrl)}
                        disabled={!thumbnail.enhancedImageUrl}
                      >
                        <span className="button-icon"></span> 
                        {thumbnail.enhancedImageUrl ? 'Preview Enhanced' : 'No Enhanced Version'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <p>No thumbnails yet</p>
              <p>Enter a YouTube URL and configure settings to generate thumbnails.</p>
            </div>
          )}
        </div>
      </div>

      {previewImage && (
        <div className="modal-overlay" onClick={() => setPreviewImage(null)}>
          <div className="modal-content enhanced-modal" onClick={(e) => e.stopPropagation()}>
            <IconButton 
              className="modal-close-button"
              onClick={() => setPreviewImage(null)}
              size="large"
              sx={{
                position: 'absolute',
                right: 8,
                top: 8,
                color: 'var(--ios-dark-gray)',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)'
                }
              }}
            >
              <CloseIcon />
            </IconButton>
            
            <img src={previewImage} alt="Enhanced Thumbnail Preview" className="modal-image" />
            
            <div className="modal-actions">
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={() => downloadImage(previewImage, true)}
                sx={{
                  backgroundColor: 'var(--ios-blue)',
                  color: 'white',
                  borderRadius: '12px',
                  padding: '10px 20px',
                  textTransform: 'none',
                  fontWeight: 500,
                  fontSize: '16px',
                  boxShadow: 'none',
                  '&:hover': {
                    backgroundColor: 'var(--ios-blue-hover)',
                    boxShadow: 'none'
                  },
                  '&:active': {
                    boxShadow: 'none'
                  }
                }}
              >
                Download Enhanced
              </Button>
            </div>
          </div>
        </div>
      )}

      {showDownloadAllModal && (
        <div className="modal-overlay" onClick={() => setShowDownloadAllModal(false)}>
          <div className="modal-content download-all-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Download All Thumbnails</h3>
              <button className="modal-close" onClick={() => setShowDownloadAllModal(false)}>
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <p>Select which version to download:</p>
              <div className="download-options">
                <button
                  className={`download-option ${downloadAllType === 'original' ? 'active' : ''}`}
                  onClick={() => setDownloadAllType('original')}
                >
                  Original Thumbnails
                </button>
                <button
                  className={`download-option ${downloadAllType === 'enhanced' ? 'active' : ''}`}
                  onClick={() => setDownloadAllType('enhanced')}
                  disabled={!thumbnails.some(t => t.enhancedImageUrl)}
                >
                  Enhanced Thumbnails
                </button>
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="cancel-button"
                onClick={() => setShowDownloadAllModal(false)}
              >
                Cancel
              </button>
              <button 
                className="confirm-download-button"
                onClick={() => {
                  handleDownloadAll();
                  setShowDownloadAllModal(false);
                }}
              >
                Download All
              </button>
            </div>
          </div>
        </div>
      )}

      {showDownloadsModal && (
        <div className="modal-overlay" onClick={() => setShowDownloadsModal(false)}>
          <div className="modal-content downloads-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Download History</h3>
              <button className="modal-close" onClick={() => setShowDownloadsModal(false)}>
                ✕
              </button>
            </div>
            
            <div className="downloads-tabs">
              <button 
                className={`tab-button ${activeDownloadsTab === 'originals' ? 'active' : ''}`}
                onClick={() => setActiveDownloadsTab('originals')}
              >
                Original Images ({downloadedOriginals.length})
              </button>
              <button 
                className={`tab-button ${activeDownloadsTab === 'enhanced' ? 'active' : ''}`}
                onClick={() => setActiveDownloadsTab('enhanced')}
              >
                Enhanced Images ({downloadedEnhanced.length})
              </button>
            </div>
            
            <div className="downloads-list-container">
              {activeDownloadsTab === 'originals' ? (
                downloadedOriginals.length > 0 ? (
                  <ul className="downloads-full-list">
                    {downloadedOriginals.map(item => (
                      <li key={item.id} className="download-full-item">
                        <div className="download-info">
                          <span className="download-filename">{item.filename}</span>
                          <span className="download-date">
                            {new Date(item.downloadedAt).toLocaleString()}
                          </span>
                        </div>
                        <span className="download-video">{item.videoTitle}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="no-downloads">No original images downloaded yet</p>
                )
              ) : (
                downloadedEnhanced.length > 0 ? (
                  <ul className="downloads-full-list">
                    {downloadedEnhanced.map(item => (
                      <li key={item.id} className="download-full-item">
                        <div className="download-info">
                          <span className="download-filename">{item.filename}</span>
                          <span className="download-date">
                            {new Date(item.downloadedAt).toLocaleString()}
                          </span>
                        </div>
                        <span className="download-video">{item.videoTitle}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="no-downloads">No enhanced images downloaded yet</p>
                )
              )}
            </div>
            
            <div className="modal-footer">
              <button 
                className="clear-all-button"
                onClick={() => {
                  clearDownloads(activeDownloadsTab === 'originals' ? 'original' : 'enhanced');
                }}
                disabled={activeDownloadsTab === 'originals' 
                  ? downloadedOriginals.length === 0 
                  : downloadedEnhanced.length === 0}
              >
                Clear {activeDownloadsTab === 'originals' ? 'Originals' : 'Enhanced'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showLogoutConfirm && (
        <div className="modal-overlay" onClick={() => setShowLogoutConfirm(false)}>
          <div className="modal-content logout-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Confirm Logout</h3>
              <button className="modal-close" onClick={() => setShowLogoutConfirm(false)}>
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <p>Are you sure you want to log out?</p>
            </div>
            
            <div className="modal-footer logout-actions">
              <button 
                className="cancel-button"
                onClick={() => setShowLogoutConfirm(false)}
              >
                Cancel
              </button>
              <button 
                className="confirm-logout-button"
                onClick={confirmLogout}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;