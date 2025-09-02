import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '@mui/material/Button';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import Modal from '@mui/material/Modal';
import TextField from '@mui/material/TextField';
import CircularProgress from '@mui/material/CircularProgress';
import Slider from '@mui/material/Slider';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import TuneIcon from '@mui/icons-material/Tune';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import FormatColorFillIcon from '@mui/icons-material/FormatColorFill';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import BlurOnIcon from '@mui/icons-material/BlurOn';
import AspectRatioIcon from '@mui/icons-material/AspectRatio';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import './AIEditScreen.css';
// import { enhanceThumbnail } from '../../services/HDRandBeautifyApi';
import API_BASE_URL from '../../config';

// Enhanced translation dictionary
const translations = {
  english: {
    // English words stay the same
    greeting: 'Hello',
    welcome: 'Welcome',
    title: 'Title',
    subscribe: 'Subscribe',
    like: 'Like',
    comment: 'Comment',
    share: 'Share',
    watch: 'Watch',
    video: 'Video',
    click: 'Click',
    here: 'Here',
    amazing: 'Amazing',
    awesome: 'Awesome',
    great: 'Great',
    cool: 'Cool',
    best: 'Best',
    quality: 'Quality',
    content: 'Content',
    channel: 'Channel',
    please: 'Please',
    subscribe_now: 'Subscribe Now',
    like_share: 'Like & Share',
    watch_now: 'Watch Now',
    click_here: 'Click Here'
  },
  hindi: {
    // Hindi translations
    greeting: 'नमस्ते',
    welcome: 'स्वागत है',
    title: 'शीर्षक',
    subscribe: 'सदस्यता लें',
    like: 'पसंद',
    comment: 'टिप्पणी',
    share: 'साझा करें',
    watch: 'देखें',
    video: 'वीडियो',
    click: 'क्लिक',
    here: 'यहां',
    amazing: 'अद्भुत',
    awesome: 'बहुत बढ़िया',
    great: 'महान',
    cool: 'ठंडा',
    best: 'सर्वश्रेष्ठ',
    quality: 'गुणवत्ता',
    content: 'सामग्री',
    channel: 'चैनल',
    please: 'कृपया',
    subscribe_now: 'अभी सब्सक्राइब करें',
    like_share: 'लाइक और शेयर करें',
    watch_now: 'अभी देखें',
    click_here: 'यहां क्लिक करें'
  }
};

const indianLanguages = [
  { code: 'hindi', label: 'Hindi' },
  { code: 'bengali', label: 'Bengali' },
  { code: 'telugu', label: 'Telugu' },
  { code: 'marathi', label: 'Marathi' },
  { code: 'tamil', label: 'Tamil' },
  { code: 'urdu', label: 'Urdu' },
  { code: 'gujarati', label: 'Gujarati' },
  { code: 'kannada', label: 'Kannada' },
  { code: 'odia', label: 'Odia' },
  { code: 'punjabi', label: 'Punjabi' },
  { code: 'malayalam', label: 'Malayalam' },
  { code: 'assamese', label: 'Assamese' },
  { code: 'maithili', label: 'Maithili' },
  { code: 'santali', label: 'Santali' },
  { code: 'kashmiri', label: 'Kashmiri' },
  { code: 'nepali', label: 'Nepali' },
];

const foreignLanguages = [
  { code: 'spanish', label: 'Spanish' },
  { code: 'french', label: 'French' },
  { code: 'german', label: 'German' },
  { code: 'chinese', label: 'Chinese' },
  { code: 'japanese', label: 'Japanese' },
  { code: 'russian', label: 'Russian' },
  { code: 'arabic', label: 'Arabic' },
];

const allLanguages = [
  { code: 'english', label: 'English', enabled: true },
  ...indianLanguages.map(l => ({ ...l, enabled: false })),
  ...foreignLanguages.map(l => ({ ...l, enabled: false })),
];

const AIEditScreen = () => {
  const [thumbnails, setThumbnails] = useState([]);
  const [, setVideoInfo] = useState(null);
  const [openModal, setOpenModal] = useState(false);
  const [currentImage, setCurrentImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [activeSlide, setActiveSlide] = useState(0);
  const [manualEditSettings, setManualEditSettings] = useState({
    brightness: 50,
    contrast: 50,
    saturation: 50,
    sharpness: 50,
    hue: 0,
    hdr: false,  // Enabled by default
    beautify: false,  // Enabled by default
    aspectRatio: '16:9'
  });
  const [textElements, setTextElements] = useState([]);
  const [currentText, setCurrentText] = useState('');
  const [language, setLanguage] = useState('english');
  const [font, setFont] = useState('Arial');
  const [textColor, setTextColor] = useState('#ffffff');
  const [textPosition, setTextPosition] = useState('top-center');
  const [logoFile, setLogoFile] = useState(null);
  const [logoSize, setLogoSize] = useState(50);
  const [logoPosition, setLogoPosition] = useState({ x: 50, y: 50 });
  const [blurRegions, setBlurRegions] = useState([]);
  const [isAddingBlur, setIsAddingBlur] = useState(false);
  const [blurIntensity, setBlurIntensity] = useState(50);
  const [showOriginal, setShowOriginal] = useState(false);
  const [, setEnhancementsApplied] = useState(false);
  const imageRef = useRef(null);
  const modalBodyRef = useRef(null);
  const navigate = useNavigate();
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancedPreviewImage, setEnhancedPreviewImage] = useState(null);
  const [rawEnhancedPreviewImage, setRawEnhancedPreviewImage] = useState(null);
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);
  const imgRef = useRef(null);
  const [imagePixelWidth, setImagePixelWidth] = useState(0);
  const [toastOpen, setToastOpen] = useState(false);

  const handlePreviewEdit = (imageUrl) => {
    setPreviewImage(imageUrl);
    setPreviewModalOpen(true);
  };

  const resetTextLogoSlide = () => {
    setTextElements([]);
    setCurrentText('');
    setLogoFile(null);
    setBlurRegions([]);
    setIsAddingBlur(false);
  };

  const resetManualEditSlide = () => {
    setManualEditSettings({
      brightness: 50,
      contrast: 50,
      saturation: 50,
      sharpness: 50,
      hue: 0,
      hdr: false,  // Enabled by default
      beautify: false,  // Enabled by default,
      aspectRatio: '16:9'
    });
    setRawEnhancedPreviewImage(null);
    setEnhancedPreviewImage(null);
  };

  // Initialize dark mode
  useEffect(() => {
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode !== null) {
      setIsDarkMode(savedMode === 'true');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(prefersDark);
    }
  }, []);

  useEffect(() => {
    if (!manualEditSettings.hdr && !manualEditSettings.beautify) {
      setEnhancedPreviewImage(null);
      setEnhancedPreviewImage(null);
    }
  }, [manualEditSettings.hdr, manualEditSettings.beautify]);

  useEffect(() => {
    if (rawEnhancedPreviewImage && (manualEditSettings.hdr || manualEditSettings.beautify)) {
      // Apply manual edits as a CSS filter for preview
      setEnhancedPreviewImage(rawEnhancedPreviewImage);
    }
  }, [
    rawEnhancedPreviewImage,
    manualEditSettings.brightness,
    manualEditSettings.contrast,
    manualEditSettings.saturation,
    manualEditSettings.hue,
    manualEditSettings.hdr,
    manualEditSettings.beautify
  ]);

  // Apply dark mode
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-theme');
      localStorage.setItem('darkMode', 'true');
    } else {
      document.body.classList.remove('dark-theme');
      localStorage.setItem('darkMode', 'false');
    }
  }, [isDarkMode]);

  // Initialize theme based on localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(prefersDark);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    async function updateEnhancedPreview() {
      if (
        rawEnhancedPreviewImage &&
        (manualEditSettings.hdr || manualEditSettings.beautify)
      ) {
        // Crop to aspect ratio if needed
        const cropped = await cropToAspectRatio(
          rawEnhancedPreviewImage,
          manualEditSettings.aspectRatio
        );
        if (isMounted) setEnhancedPreviewImage(cropped);
      }
    }
    updateEnhancedPreview();
    return () => { isMounted = false; };
  }, [
    rawEnhancedPreviewImage,
    manualEditSettings.aspectRatio,
    manualEditSettings.hdr,
    manualEditSettings.beautify
  ]);

  // Apply the theme to the body element
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-theme');
      document.body.classList.remove('light-theme');
    } else {
      document.body.classList.add('light-theme');
      document.body.classList.remove('dark-theme');
    }
  }, [isDarkMode]);

  useEffect(() => {
    const userEmail = localStorage.getItem('userEmail');
    if (userEmail) {
      const savedTheme = JSON.parse(localStorage.getItem(`userTheme_${userEmail}`));
      setIsDarkMode(savedTheme || false);

      if (savedTheme) {
        document.body.classList.add('dark-theme');
      } else {
        document.body.classList.remove('dark-theme');
      }
    }
  }, []);

  const handleThemeToggle = () => {
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

  // Load saved thumbnails
  useEffect(() => {
    const savedData = JSON.parse(localStorage.getItem('aiEditThumbnails'));
    if (savedData && savedData.thumbnails && savedData.thumbnails.length > 0) {
      const thumbnailsWithOriginal = savedData.thumbnails.map(thumb => ({
        ...thumb,
        displayImage: thumb.imageUrl
      }));
      setThumbnails(thumbnailsWithOriginal);
      setVideoInfo(savedData.videoInfo);
    } else {
      navigate('/home');
    }
  }, [navigate]);

  const formatTime = (timeStr) => {
    if (!timeStr) return '0:00';
    const time = String(timeStr); 
    if (time.includes(':')) return time;
    const seconds = parseInt(time, 10); 
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleEditClick = async (thumbnail) => {
    setCurrentImage(thumbnail);
    setActiveSlide(0);
    setOpenModal(true);
    setManualEditSettings({
      brightness: 50,
      contrast: 50,
      saturation: 50,
      sharpness: 50,
      hue: 0,
      hdr: false,  // Enabled by default
      beautify: false,  // Enabled by default
      aspectRatio: '16:9'
    });
    setTextElements([]);
    setCurrentText('');
    setBlurRegions([]);
    setIsAddingBlur(false);
    setShowOriginal(false);
    setLogoFile(null);
  };

  function cropToAspectRatio(imageSrc, aspectRatio) {
  return new Promise((resolve) => {
    if (!aspectRatio || aspectRatio === 'Original') {
      resolve(imageSrc);
      return;
    }
    const [ratioW, ratioH] = aspectRatio.split(':').map(Number);
    const img = new window.Image();
    img.src = imageSrc;
    img.onload = () => {
      const targetRatio = ratioW / ratioH;
      const currentRatio = img.width / img.height;
      let sx = 0, sy = 0, sw = img.width, sh = img.height;
      if (currentRatio > targetRatio) {
        // Crop sides
        sw = img.height * targetRatio;
        sx = (img.width - sw) / 2;
      } else {
        // Crop top/bottom
        sh = img.width / targetRatio;
        sy = (img.height - sh) / 2;
      }
      const canvas = document.createElement('canvas');
      canvas.width = sw;
      canvas.height = sh;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh);
      resolve(canvas.toDataURL('image/png'));
    };
  });
}

  // Enhanced translation function
  const translateText = (text, targetLang) => {
    if (targetLang === 'english') return text;
    
    // Split text into words and translate each word if possible
    const words = text.split(' ');
    const translatedWords = words.map(word => {
      // Remove punctuation for matching
      const cleanWord = word.replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, '').toLowerCase();
      const translated = translations[targetLang][cleanWord] || word;
      
      // Preserve capitalization of first letter
      if (word[0] === word[0]?.toUpperCase()) {
        return translated.charAt(0).toUpperCase() + translated.slice(1);
      }
      return translated;
    });
    
    return translatedWords.join(' ');
  };

  const applyClientSideFilters = (imageUrl, settings) => {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const img = new Image();
      img.crossOrigin = 'Anonymous';
      img.src = imageUrl;
      
      img.onload = () => {
        // Apply aspect ratio first
        let drawWidth = img.width;
        let drawHeight = img.height;
        let offsetX = 0;
        let offsetY = 0;

        if (settings.aspectRatio && settings.aspectRatio !== 'Original') {
          const [ratioW, ratioH] = settings.aspectRatio.split(':').map(Number);
          const targetRatio = ratioW / ratioH;
          const currentRatio = img.width / img.height;

          if (currentRatio > targetRatio) {
            // Image is wider than target ratio - crop sides
            drawWidth = img.height * targetRatio;
            offsetX = (img.width - drawWidth) / 2;
          } else {
            // Image is taller than target ratio - crop top/bottom
            drawHeight = img.width / targetRatio;
            offsetY = (img.height - drawHeight) / 2;
          }
        }

        canvas.width = settings.aspectRatio === 'Original' ? img.width : drawWidth;
        canvas.height = settings.aspectRatio === 'Original' ? img.height : drawHeight;
        const ctx = canvas.getContext('2d');
        
        // Draw original image first with aspect ratio crop
        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight, 0, 0, canvas.width, canvas.height);
        
        // Apply basic adjustments
        ctx.filter = `
          brightness(${(settings.brightness / 50)})
          contrast(${(settings.contrast / 50)})
          saturate(${(settings.saturation / 50)})
          hue-rotate(${settings.hue}deg)
        `;
        ctx.drawImage(canvas, 0, 0);
        ctx.filter = 'none';
        
        // Apply sharpness (unsharp mask)
        if (settings.sharpness > 50) {
          const tempCanvas = document.createElement('canvas');
          tempCanvas.width = canvas.width;
          tempCanvas.height = canvas.height;
          const tempCtx = tempCanvas.getContext('2d');
          
          // Create a blurred version
          const blurAmount = (100 - settings.sharpness) / 50;
          tempCtx.filter = `blur(${blurAmount}px)`;
          tempCtx.drawImage(canvas, 0, 0);
          
          // Blend with original using overlay
          ctx.globalCompositeOperation = 'overlay';
          ctx.globalAlpha = 0.5;
          ctx.drawImage(tempCanvas, 0, 0);
          ctx.globalCompositeOperation = 'source-over';
          ctx.globalAlpha = 1.0;
        }
        
        // Apply HDR effect
        if (settings.hdr) {
          const tempCanvas = document.createElement('canvas');
          tempCanvas.width = canvas.width;
          tempCanvas.height = canvas.height;
          const tempCtx = tempCanvas.getContext('2d');
          
          // Create high contrast version
          tempCtx.filter = 'contrast(200%) brightness(110%) saturate(120%)';
          tempCtx.drawImage(canvas, 0, 0);
          
          // Blend with original using overlay
          ctx.globalCompositeOperation = 'overlay';
          ctx.globalAlpha = 0.3;
          ctx.drawImage(tempCanvas, 0, 0);
          ctx.globalCompositeOperation = 'source-over';
          ctx.globalAlpha = 1.0;
        }
        
        // Apply beautify effect (skin smoothing)
        if (settings.beautify) {
          const tempCanvas = document.createElement('canvas');
          tempCanvas.width = canvas.width;
          tempCanvas.height = canvas.height;
          const tempCtx = tempCanvas.getContext('2d');
          
          // Create a blurred version for skin areas
          tempCtx.filter = 'blur(8px)';
          tempCtx.drawImage(canvas, 0, 0);
          
          // Create skin mask (simplified skin tone detection)
          const skinCanvas = document.createElement('canvas');
          skinCanvas.width = canvas.width;
          skinCanvas.height = canvas.height;
          const skinCtx = skinCanvas.getContext('2d');
          skinCtx.drawImage(canvas, 0, 0);
          
          const imageData = skinCtx.getImageData(0, 0, skinCanvas.width, skinCanvas.height);
          const data = imageData.data;
          
          for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            // Enhanced skin tone detection
            if (r > 95 && g > 40 && b > 20 && 
                r > g && r > b && 
                Math.abs(r - g) > 15 && 
                r - b > 15 &&
                !(Math.abs(r - g) <= 5 && r > 200 && g > 200 && b > 200)) {
              // Keep as is (skin area)
            } else {
              // Non-skin area - make transparent
              data[i + 3] = 0;
            }
          }
          
          skinCtx.putImageData(imageData, 0, 0);
          
          // Apply the blurred version only to skin areas
          ctx.drawImage(tempCanvas, 0, 0);
          ctx.globalCompositeOperation = 'destination-in';
          ctx.drawImage(skinCanvas, 0, 0);
          ctx.globalCompositeOperation = 'source-over';
          
          // Blend with original
          ctx.globalAlpha = 0.7;
          ctx.drawImage(canvas, 0, 0);
          ctx.globalAlpha = 1.0;
        }
        
        resolve(canvas.toDataURL('image/jpeg', 0.9));
      };
    });
  };

  // Apply aspect ratio to the displayed image
  const applyAspectRatioToDisplay = (imageUrl, aspectRatio) => {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const img = new Image();
      img.crossOrigin = 'Anonymous';
      img.src = imageUrl;
      
      img.onload = () => {
        let drawWidth = img.width;
        let drawHeight = img.height;
        let offsetX = 0;
        let offsetY = 0;

        if (aspectRatio && aspectRatio !== 'Original') {
          const [ratioW, ratioH] = aspectRatio.split(':').map(Number);
          const targetRatio = ratioW / ratioH;
          const currentRatio = img.width / img.height;

          if (currentRatio > targetRatio) {
            drawWidth = img.height * targetRatio;
            offsetX = (img.width - drawWidth) / 2;
          } else {
            drawHeight = img.width / targetRatio;
            offsetY = (img.height - drawHeight) / 2;
          }
        }

        canvas.width = aspectRatio === 'Original' ? img.width : drawWidth;
        canvas.height = aspectRatio === 'Original' ? img.height : drawHeight;
        const ctx = canvas.getContext('2d');
        
        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL('image/jpeg', 0.9));
      };
    });
  };

  const handleUpscaleAndDownload = async () => {
    if (!currentImage) return;

    setIsProcessing(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Authentication token not found');

      // Determine if we're using original or edited image
      const useOriginal = showOriginal ||
        (textElements.length === 0 &&
          !logoFile &&
          blurRegions.length === 0 &&
          activeSlide !== 1);

      if (useOriginal) {
        // Original image case - use thumbnail_url
        let relativeThumbnailUrl = currentImage.imageUrl.startsWith('http')
          ? new URL(currentImage.imageUrl).pathname
          : currentImage.imageUrl;

        const formData = new FormData();
        formData.append('thumbnail_url', relativeThumbnailUrl);

        const response = await fetch(`${API_BASE_URL}accounts/singleUpscale/`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData
        });

        if (!response.ok) throw new Error(await response.text());

        // Handle download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `upscaled_original_${Date.now()}.jpg`;
        link.click();
        window.URL.revokeObjectURL(url);
      } else {
        // Edited image case - create canvas and upload
        const img = new Image();
        img.crossOrigin = 'Anonymous';
        img.src = currentImage.displayImage || currentImage.imageUrl;
        await new Promise((resolve) => img.onload = resolve);

        const naturalWidth = img.naturalWidth || img.width;
        const naturalHeight = img.naturalHeight || img.height;

        const canvas = document.createElement('canvas');
        canvas.width = naturalWidth;
        canvas.height = naturalHeight;
        const ctx = canvas.getContext('2d');

        // Draw the image at its natural size
        ctx.drawImage(img, 0, 0, naturalWidth, naturalHeight);

        // Always apply manual edits if not showing original and on slide 1
        if (
          !showOriginal &&
          activeSlide === 1
        ) {
          ctx.filter = `
            brightness(${manualEditSettings.brightness / 50})
            contrast(${manualEditSettings.contrast / 50})
            saturate(${manualEditSettings.saturation / 50})
            hue-rotate(${manualEditSettings.hue}deg)
          `;
          ctx.drawImage(canvas, 0, 0);
          ctx.filter = 'none';
        }

        // --- Draw blur regions BEFORE overlays ---
        blurRegions.forEach(region => {
          const x = (region.x / 100) * canvas.width;
          const y = (region.y / 100) * canvas.height;
          const width = (region.width / 100) * canvas.width;
          const height = (region.height / 100) * canvas.height;

          const tempCanvas = document.createElement('canvas');
          tempCanvas.width = width;
          tempCanvas.height = height;
          const tempCtx = tempCanvas.getContext('2d');

          tempCtx.drawImage(
            canvas,
            x - width / 2, y - height / 2, width, height,
            0, 0, width, height
          );

          tempCtx.filter = `blur(${region.intensity / 10}px)`;
          tempCtx.drawImage(tempCanvas, 0, 0);

          ctx.drawImage(
            tempCanvas,
            0, 0, width, height,
            x - width / 2, y - height / 2, width, height
          );
        });

        // Draw text elements
        textElements.forEach(text => {
          ctx.font = `${text.fontSize || 20}px ${text.font}`;
          ctx.fillStyle = text.color;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          const x = (text.x / 100) * canvas.width;
          const y = (text.y / 100) * canvas.height;
          ctx.fillText(text.text, x, y);
        });

        // Draw logo if exists
        if (logoFile) {
          const logoImg = new Image();
          logoImg.src = URL.createObjectURL(logoFile);
          await new Promise((resolve) => { logoImg.onload = resolve; });

          const logoWidth = (logoSize / 100) * canvas.width;
          const aspect = logoImg.width / logoImg.height || 1;
          const logoHeight = logoWidth / aspect;

          const logoX = (logoPosition.x / 100) * canvas.width;
          const logoY = (logoPosition.y / 100) * canvas.height;
          ctx.drawImage(
            logoImg,
            logoX - logoWidth / 2,
            logoY - logoHeight / 2,
            logoWidth,
            logoHeight
          );
        }

        // Convert canvas to blob
        const blob = await new Promise(resolve =>
          canvas.toBlob(resolve, 'image/jpeg', 0.9)
        );

        // Upload edited image
        const formData = new FormData();
        formData.append('image', blob, 'edited-thumbnail.jpg');

        const response = await fetch(`${API_BASE_URL}accounts/singleUpscale/`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData
        });

        if (!response.ok) throw new Error(await response.text());

        // Handle download
        const upscaledBlob = await response.blob();
        const url = window.URL.createObjectURL(upscaledBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `upscaled_edited_${Date.now()}.jpg`;
        link.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Upscale error:', error);
      setError(error.message || 'Failed to upscale image');
    } finally {
      setIsProcessing(false);
    }
  };

  // Update displayed image when aspect ratio changes
  useEffect(() => {
  if (currentImage && activeSlide === 1 && !isEnhancing) {
    const updateImage = async () => {
      const newImageUrl = await applyAspectRatioToDisplay(
        currentImage.imageUrl,
        manualEditSettings.aspectRatio
      );
      setCurrentImage((prev) => ({
        ...prev,
        displayImage: newImageUrl,
      }));
    };
    updateImage();
  }
}, [manualEditSettings.aspectRatio, activeSlide, currentImage, isEnhancing]); // Add 'currentImage' here

  useEffect(() => {
    if (currentImage && activeSlide === 1) {
      const updateImage = async () => {
        const newImageUrl = await applyAspectRatioToDisplay(
          currentImage.imageUrl, 
          manualEditSettings.aspectRatio
        );
        setCurrentImage(prev => ({
          ...prev,
          displayImage: newImageUrl
        }));
      };
      updateImage();
    }
  }, [manualEditSettings.aspectRatio, activeSlide, currentImage]); // Include 'currentImage' here

  useEffect(() => {
    if (activeSlide !== 1) {
      setEnhancementsApplied(false);
    }
  }, [activeSlide]);

  useEffect(() => {
    console.log('Current Image Updated:', currentImage);
  }, [currentImage]);

  const handleDownload = async () => {
    if (!currentImage) return;

    setIsProcessing(true);
    try {
      // Load the image to get its natural size
      const img = new Image();
      img.crossOrigin = 'Anonymous';
      if (
        activeSlide === 1 &&
        (manualEditSettings.hdr || manualEditSettings.beautify) &&
        rawEnhancedPreviewImage
      ) {
        img.src = rawEnhancedPreviewImage;
      } else {
        img.src = showOriginal ? currentImage.imageUrl : (currentImage.displayImage || currentImage.imageUrl);
      }
      await new Promise((resolve) => { img.onload = resolve; });

      // Use the natural size of the image for the canvas
      const naturalWidth = img.naturalWidth || img.width;
      const naturalHeight = img.naturalHeight || img.height;

      const canvas = document.createElement('canvas');
      canvas.width = naturalWidth;
      canvas.height = naturalHeight;
      const ctx = canvas.getContext('2d');

      // Draw the image at its natural size
      ctx.drawImage(img, 0, 0, naturalWidth, naturalHeight);

      // Always apply manual edits if not showing original and on slide 1
      if (
        !showOriginal &&
        activeSlide === 1
      ) {
        ctx.filter = `
          brightness(${manualEditSettings.brightness / 50})
          contrast(${manualEditSettings.contrast / 50})
          saturate(${manualEditSettings.saturation / 50})
          hue-rotate(${manualEditSettings.hue}deg)
        `;
        ctx.drawImage(canvas, 0, 0);
        ctx.filter = 'none';
      }

      // --- Draw blur regions BEFORE overlays ---
      blurRegions.forEach(region => {
        const x = (region.x / 100) * canvas.width;
        const y = (region.y / 100) * canvas.height;
        const width = (region.width / 100) * canvas.width;
        const height = (region.height / 100) * canvas.height;

        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = width;
        tempCanvas.height = height;
        const tempCtx = tempCanvas.getContext('2d');

        tempCtx.drawImage(
          canvas,
          x - width / 2, y - height / 2, width, height,
          0, 0, width, height
        );

        tempCtx.filter = `blur(${region.intensity / 10}px)`;
        tempCtx.drawImage(tempCanvas, 0, 0);

        ctx.drawImage(
          tempCanvas,
          0, 0, width, height,
          x - width / 2, y - height / 2, width, height
        );
      });

      // Draw text elements
      textElements.forEach(text => {
        ctx.font = `${text.fontSize || 20}px ${text.font}`;
        ctx.fillStyle = text.color;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const x = (text.x / 100) * canvas.width;
        const y = (text.y / 100) * canvas.height;
        ctx.fillText(text.text, x, y);
      });

      // Draw logo if exists
      if (logoFile) {
        const logoImg = new Image();
        logoImg.src = URL.createObjectURL(logoFile);

        await new Promise((resolve) => {
          logoImg.onload = resolve;
        });

        // Use percentage of canvas for logo size
        const logoWidth = (logoSize / 100) * canvas.width;
        const aspect = logoImg.width / logoImg.height || 1;
        const logoHeight = logoWidth / aspect;

        const logoX = (logoPosition.x / 100) * canvas.width;
        const logoY = (logoPosition.y / 100) * canvas.height;
        ctx.drawImage(
          logoImg,
          logoX - logoWidth / 2,
          logoY - logoHeight / 2,
          logoWidth,
          logoHeight
        );
      }

      // Create download link
      const link = document.createElement('a');
      link.download = `thumbnail-${currentImage.timestamp || Date.now()}.jpg`;
      link.href = canvas.toDataURL('image/jpeg', 0.9);
      link.click();
    } catch (err) {
      console.error('Error generating download:', err);
      setError('Failed to generate download. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  // ...existing code...
const handleApplyEdit = async () => {
  if (activeSlide === 0 && textElements.length === 0 && !logoFile && blurRegions.length === 0) {
    setError('Please add some text, a logo, or blur regions');
    return;
  }

  setIsProcessing(true);
  setError(null);

  try {
    // Generate the edited image WITH overlays
    const editedImageUrl = await generateEditedImageWithOverlays(currentImage, {
      textElements,
      logoFile,
      logoSize,
      logoPosition,
      blurRegions,
      manualEditSettings,
      showOriginal,
      activeSlide,
      rawEnhancedPreviewImage,
    });

    setThumbnails(prev =>
      prev.map(thumb =>
        thumb.id === currentImage.id
          ? { ...thumb, appliedEditImage: editedImageUrl }
          : thumb
      )
    );
    setOpenModal(false);  
    setActiveSlide(0);
  } catch (err) {
    console.error('Error applying edit:', err);
    setError('An error occurred while applying your edit.');
  } finally {
    setIsProcessing(false);
  }
};
// ...existing code...

  const handleCloseModal = () => {
    setOpenModal(false);
    setError(null);
    setActiveSlide(0);
    setTextElements([]);
    setLogoFile(null);
    setBlurRegions([]);
    setIsAddingBlur(false);
    setShowOriginal(false);
  };

  const handleNextSlide = () => {
    setActiveSlide(prev => Math.min(prev + 1, 2));
    setError(null);
  };

  const handlePrevSlide = () => {
    setActiveSlide(prev => Math.max(prev - 1, 0));
    setError(null);
  };

  const handleSettingChange = async (setting, value) => {
  const newSettings = {
    ...manualEditSettings,
    [setting]: value,
  };
  setManualEditSettings(newSettings);

  if (activeSlide === 1 && (setting === 'hdr' || setting === 'beautify')) {
    if (!newSettings.hdr && !newSettings.beautify) {
      setEnhancedPreviewImage(null);
      return;
    }
    setIsProcessing(true);
    setIsEnhancing(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Authentication token not found');

      let relativeThumbnailUrl;
      try {
        const imageUrl = new URL(currentImage.imageUrl);
        relativeThumbnailUrl = imageUrl.pathname;
      } catch (e) {
        relativeThumbnailUrl = currentImage.imageUrl;
      }

      console.log('Sending API request with:', { thumbnail_url: relativeThumbnailUrl, hdr: newSettings.hdr, beautify: newSettings.beautify });

      const formData = new FormData();
      formData.append('thumbnail_url', relativeThumbnailUrl);
      formData.append('hdr', newSettings.hdr);
      formData.append('beautify', newSettings.beautify);

      const response = await fetch(`${API_BASE_URL}accounts/enhance_thumbnailhdr/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', errorText);
        throw new Error(errorText);
      }

      const arrayBuffer = await response.arrayBuffer();
      console.log('ArrayBuffer length:', arrayBuffer.byteLength);
      const base64Image = `data:image/png;base64,${btoa(
        new Uint8Array(arrayBuffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
      )}`;
      console.log('Base64 Image:', base64Image.substring(0, 100) + '...');

      setRawEnhancedPreviewImage(base64Image);
    } catch (err) {
      console.error(`Error applying ${setting}:`, err);
      setError(`Failed to apply ${setting === 'hdr' ? 'HDR' : 'Beautify'}. Please try again.`);
    } finally {
      setIsProcessing(false);
      setIsEnhancing(false); // Reset enhancing flag
    }
  }
};

  const addTextElement = () => {
    if (!currentText.trim()) return;
    
    const translatedText = language === 'hindi' ? 
      translateText(currentText, 'hindi') : currentText;
    
    // Calculate initial position based on selected position
    let x, y;
    switch(textPosition) {
      case 'top-left': x = 15; y = 15; break;
      case 'top-center': x = 50; y = 15; break;
      case 'top-right': x = 85; y = 15; break;
      case 'center-left': x = 15; y = 50; break;
      case 'center': x = 50; y = 50; break;
      case 'center-right': x = 85; y = 50; break;
      case 'bottom-left': x = 15; y = 85; break;
      case 'bottom-center': x = 50; y = 85; break;
      case 'bottom-right': x = 85; y = 85; break;
      default: x = 50; y = 50;
    }
    
    const newTextElement = {
      id: Date.now(),
      text: translatedText,
      font,
      color: textColor,
      position: textPosition,
      x,
      y,
      isDragging: false
    };
    
    setTextElements([...textElements, newTextElement]);
    setCurrentText('');
  };

  const handleLogoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setLogoFile(file);
      setLogoPosition({ x: 50, y: 50 });
      setLogoSize(20); // Set initial size to 20% of the image width
    }
  };

  const handleImageClick = (e) => {
    if (!isAddingBlur || !imageRef.current) return;
    
    const rect = imageRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    const newBlurRegion = {
      id: Date.now(),
      x,
      y,
      width: 15,
      height: 15,
      intensity: blurIntensity
    };
    
    setBlurRegions([...blurRegions, newBlurRegion]);
    setIsAddingBlur(false);
  };

  const handleDragStart = (e, id, type) => {
    e.dataTransfer.setData('application/json', JSON.stringify({ id, type }));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    try {
      const data = JSON.parse(e.dataTransfer.getData('application/json'));
      if (!imageRef.current) return;
      
      const rect = imageRef.current.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      
      const clampedX = Math.max(5, Math.min(x, 95));
      const clampedY = Math.max(5, Math.min(y, 95));
      
      if (data.type === 'text') {
        setTextElements(textElements.map(text => 
          text.id === data.id ? { ...text, x: clampedX, y: clampedY } : text
        ));
      } else if (data.type === 'logo') {
        setLogoPosition({ x: clampedX, y: clampedY });
      } else if (data.type === 'blur') {
        setBlurRegions(blurRegions.map(region => 
          region.id === data.id ? { ...region, x: clampedX, y: clampedY } : region
        ));
      }
    } catch (err) {
      console.error('Error handling drop:', err);
    }
  };

  const removeTextElement = (id) => {
    setTextElements(textElements.filter(text => text.id !== id));
  };

  const removeLogo = () => {
    setLogoFile(null);
  };

  const removeBlurRegion = (id) => {
    setBlurRegions(blurRegions.filter(region => region.id !== id));
  };

  const toggleBlurMode = () => {
    setIsAddingBlur(!isAddingBlur);
  };

  const handleResizeStart = (e, id) => {
    e.preventDefault();
    const startX = e.clientX;
    const startY = e.clientY;
  
    const region = blurRegions.find((region) => region.id === id);
    const initialWidth = region.width;
    const initialHeight = region.height;
  
    const handleMouseMove = (moveEvent) => {
      const deltaX = ((moveEvent.clientX - startX) / imageRef.current.offsetWidth) * 100;
      const deltaY = ((moveEvent.clientY - startY) / imageRef.current.offsetHeight) * 100;
  
      setBlurRegions((prevRegions) =>
        prevRegions.map((region) =>
          region.id === id
            ? {
                ...region,
                width: Math.max(5, initialWidth + deltaX),
                height: Math.max(5, initialHeight + deltaY),
              }
            : region
        )
      );
    };
  
    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleTextResizeStart = (e, id) => {
    e.preventDefault();
    const startX = e.clientX;
  
    const textElement = textElements.find((text) => text.id === id);
    const initialFontSize = textElement.fontSize || 20;
  
    const handleMouseMove = (moveEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const newFontSize = Math.max(10, initialFontSize + deltaX / 5); // Adjust scaling factor as needed
  
      setTextElements((prevTextElements) =>
        prevTextElements.map((text) =>
          text.id === id
            ? {
                ...text,
                fontSize: newFontSize,
              }
            : text
        )
      );
    };
  
    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // const handleLanguageChange = (e) => {
  //   const value = e.target.value;
  //   if (value === 'english') {
  //     setLanguage(value);
  //   } else {
  //     setToastOpen(true);
  //   }
  // };

  const handleToastClose = (event, reason) => {
    if (reason === 'clickaway') return;
    setToastOpen(false);
  };

  // Modal slide titles
  const slideLabels = ["Text & Logo", "Manual Edit", "AI Enhancement"];
  const slideIcons = [<FormatColorFillIcon />, <TuneIcon />, <AutoFixHighIcon />];

  const fonts = ['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana', 'Georgia'];
  const colors = ['#ffffff', '#000000', '#ff0000', '#00ff00', '#0000ff', '#ffff00'];
  const positions = [
    'top-left', 'top-center', 'top-right',
    'center-left', 'center', 'center-right',
    'bottom-left', 'bottom-center', 'bottom-right'
  ];
  const aspectRatios = ['16:9', '1:1', '4:5', '9:16', 'Original'];

//   useEffect(() => {
//   async function updatePreview() {
//     let baseImage;
//     if (rawEnhancedPreviewImage && (manualEditSettings.hdr || manualEditSettings.beautify)) {
//       baseImage = rawEnhancedPreviewImage;
//     } else if (currentImage) {
//       baseImage = currentImage.displayImage || currentImage.imageUrl;
//     }
//     if (baseImage) {
//       const preview = await applyClientSideFilters(baseImage, manualEditSettings);
//       setEnhancedPreviewImage(preview);
//     }
//   }
//   if (activeSlide === 1 && currentImage) {
//     updatePreview();
//   }
//   // eslint-disable-next-line
// }, [
//   rawEnhancedPreviewImage,
//   manualEditSettings.brightness,
//   manualEditSettings.contrast,
//   manualEditSettings.saturation,
//   manualEditSettings.hue,
//   manualEditSettings.sharpness,
//   manualEditSettings.aspectRatio,
//   manualEditSettings.hdr,
//   manualEditSettings.beautify,
//   currentImage,
//   activeSlide
// ]);

useEffect(() => {
  async function updatePreview() {
    if (rawEnhancedPreviewImage && (manualEditSettings.hdr || manualEditSettings.beautify)) {
      // Always crop the server image to the selected aspect ratio
      const cropped = await cropToAspectRatio(
        rawEnhancedPreviewImage,
        manualEditSettings.aspectRatio
      );
      setEnhancedPreviewImage(cropped);
    } else if (currentImage) {
      // Only apply client-side filters to the original
      const preview = await applyClientSideFilters(
        currentImage.displayImage || currentImage.imageUrl,
        manualEditSettings
      );
      setEnhancedPreviewImage(preview);
    }
  }
  if (currentImage) {
    updatePreview();
  }
  // eslint-disable-next-line
}, [
  rawEnhancedPreviewImage,
  manualEditSettings.brightness,
  manualEditSettings.contrast,
  manualEditSettings.saturation,
  manualEditSettings.hue,
  manualEditSettings.sharpness,
  manualEditSettings.aspectRatio,
  manualEditSettings.hdr,
  manualEditSettings.beautify,
  currentImage,
  activeSlide
]);

  async function generateEditedImageWithOverlays(imageObj, options = {}) {
  // imageObj: { imageUrl, displayImage, ... }
  // options: { textElements, logoFile, logoSize, logoPosition, blurRegions, manualEditSettings, showOriginal, activeSlide, rawEnhancedPreviewImage }
  return new Promise(async (resolve) => {
    const {
      textElements = [],
      logoFile = null,
      logoSize = 50,
      logoPosition = { x: 50, y: 50 },
      blurRegions = [],
      manualEditSettings = {},
      showOriginal = false,
      activeSlide = 0,
      rawEnhancedPreviewImage = null,
    } = options;

    // Choose base image
    let imgSrc = imageObj.displayImage || imageObj.imageUrl;
    if (
      activeSlide === 1 &&
      (manualEditSettings.hdr || manualEditSettings.beautify) &&
      rawEnhancedPreviewImage
    ) {
      imgSrc = rawEnhancedPreviewImage;
    } else if (showOriginal) {
      imgSrc = imageObj.imageUrl;
    }

    const img = new window.Image();
    img.crossOrigin = 'Anonymous';
    img.src = imgSrc;
    await new Promise((resolveImg) => (img.onload = resolveImg));

    const naturalWidth = img.naturalWidth || img.width;
    const naturalHeight = img.naturalHeight || img.height;

    const canvas = document.createElement('canvas');
    canvas.width = naturalWidth;
    canvas.height = naturalHeight;
    const ctx = canvas.getContext('2d');

    // Draw base image
    ctx.drawImage(img, 0, 0, naturalWidth, naturalHeight);

    // Manual edits (if needed)
    if (!showOriginal && activeSlide === 1) {
      ctx.filter = `
        brightness(${manualEditSettings.brightness / 50})
        contrast(${manualEditSettings.contrast / 50})
        saturate(${manualEditSettings.saturation / 50})
        hue-rotate(${manualEditSettings.hue}deg)
      `;
      ctx.drawImage(canvas, 0, 0);
      ctx.filter = 'none';
    }

    // Blur regions
    blurRegions.forEach(region => {
      const x = (region.x / 100) * canvas.width;
      const y = (region.y / 100) * canvas.height;
      const width = (region.width / 100) * canvas.width;
      const height = (region.height / 100) * canvas.height;

      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = width;
      tempCanvas.height = height;
      const tempCtx = tempCanvas.getContext('2d');

      tempCtx.drawImage(
        canvas,
        x - width / 2, y - height / 2, width, height,
        0, 0, width, height
      );

      tempCtx.filter = `blur(${region.intensity / 10}px)`;
      tempCtx.drawImage(tempCanvas, 0, 0);

      ctx.drawImage(
        tempCanvas,
        0, 0, width, height,
        x - width / 2, y - height / 2, width, height
      );
    });

    // Text overlays
    textElements.forEach(text => {
      ctx.font = `${text.fontSize || 20}px ${text.font}`;
      ctx.fillStyle = text.color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const x = (text.x / 100) * canvas.width;
      const y = (text.y / 100) * canvas.height;
      ctx.fillText(text.text, x, y);
    });

    // Logo overlay
    if (logoFile) {
      const logoImg = new window.Image();
      logoImg.src = URL.createObjectURL(logoFile);
      await new Promise((resolveLogo) => (logoImg.onload = resolveLogo));
      const logoWidth = (logoSize / 100) * canvas.width;
      const aspect = logoImg.width / logoImg.height || 1;
      const logoHeight = logoWidth / aspect;
      const logoX = (logoPosition.x / 100) * canvas.width;
      const logoY = (logoPosition.y / 100) * canvas.height;
      ctx.drawImage(
        logoImg,
        logoX - logoWidth / 2,
        logoY - logoHeight / 2,
        logoWidth,
        logoHeight
      );
    }

    resolve(canvas.toDataURL('image/jpeg', 0.9));
  });
}

  return (
    <div className="ai-edit-container">
      <div className="ai-edit-header">
        <Button 
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/home')}
          sx={{ 
            color: 'var(--ios-blue)',
            textTransform: 'none',
            fontWeight: 500
          }}
        >
          Back
        </Button>
        <h1 className="ai-edit-title">Edit Thumbnails</h1>
        <button 
          className="ai-theme-toggle"
          onClick={handleThemeToggle}
          aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </button>
      </div>

      <div className="ai-thumbnails-container">
        {thumbnails.length > 0 ? (
          <div className="ai-thumbnails-grid">
            {thumbnails.map((thumbnail) => (
              <div key={thumbnail.id} className="ai-thumbnail-card">
                <div className="ai-thumbnail-image-container">
                  <img 
                    src={thumbnail.displayImage} 
                    alt={`Thumbnail at ${thumbnail.timestamp}`} 
                    className="ai-thumbnail-image"
                  />
                  <div className="ai-thumbnail-timestamp">
                    {formatTime(thumbnail.timestamp || 0)}
                  </div>
                </div>
                <div className="ai-thumbnail-details">
                  <div className="ai-thumbnail-emotion">
                    <span className={`ai-emotion-badge ${thumbnail.emotion.toLowerCase()}`}>
                      {thumbnail.emotion}
                    </span>
                    <span className="ai-face-coverage">{thumbnail.faceCoverage}% face</span>
                  </div>
                </div>
                <div className="ai-thumbnail-actions" style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
                <button
                  className="ai-screen-edit-button"
                  onClick={() => handleEditClick(thumbnail)}
                  style={{
                    background: 'var(--ios-blue)',
                    color: 'white',
                    border: 'none',
                    borderRadius: 8,
                    padding: '6px 16px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    marginRight: 0,
                    display: 'inline-flex',
                    alignItems: 'center',
                    transition: 'background 0.2s, width 0.3s cubic-bezier(.4,2,.6,1), padding 0.3s cubic-bezier(.4,2,.6,1)',
                    width: thumbnail.appliedEditImage ? 110 : 160, // animate width
                    minWidth: 0,
                    overflow: 'hidden',
                  }}
                  onMouseOver={e => e.currentTarget.style.background = 'var(--ios-blue-hover)'}
                  onMouseOut={e => e.currentTarget.style.background = 'var(--ios-blue)'}
                >
                  <EditIcon fontSize="small" sx={{ mr: 0.5 }} />
                  <span style={{
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    transition: 'opacity 0.2s',
                    opacity: 1
                  }}>
                    {thumbnail.enhancedImageUrl ? 'AI Touch-Up' : 'Edit'}
                  </span>
                </button>
                <div style={{
                  width: thumbnail.appliedEditImage ? 'auto' : 0,
                  opacity: thumbnail.appliedEditImage ? 1 : 0,
                  marginLeft: thumbnail.appliedEditImage ? 8 : 0,
                  transition: 'width 0.3s cubic-bezier(.4,2,.6,1), opacity 0.3s, margin-left 0.3s',
                  overflow: 'hidden',
                  display: 'inline-block'
                }}>
                  {thumbnail.appliedEditImage && (
                    <button
                      className="ai-preview-edit-button"
                      onClick={() => handlePreviewEdit(thumbnail.appliedEditImage)}
                      style={{
                        background: 'var(--ios-blue)',
                        color: 'white',
                        border: '2px solid var(--ios-blue)',
                        borderRadius: 8,
                        padding: '6px 16px',
                        fontWeight: 500,
                        cursor: 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        transition: 'background 0.2s, color 0.2s',
                      }}
                      onMouseOver={e => {
                        e.currentTarget.style.background = 'black';
                        e.currentTarget.style.color = 'white';
                      }}
                      onMouseOut={e => {
                        e.currentTarget.style.background = 'white';
                        e.currentTarget.style.color = 'var(--ios-blue)';
                      }}
                    >
                      Preview
                    </button>
                  )}
                </div>
              </div>

              </div>
            ))}
          </div>
        ) : (
          <div className="ai-empty-state">
            <p>No thumbnails selected</p>
          </div>
        )}
      </div>

      {/* Multi-Slide Edit Modal */}
      <Modal
        open={openModal}
        onClose={handleCloseModal}
        aria-labelledby="edit-modal-title"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'auto'
        }}
      >
        <div className="ai-edit-modal">
          {/* Modal Header */}
          <div className="ai-modal-header">
            <h2 id="edit-modal-title">Edit Thumbnail</h2>
            <div className="ai-modal-progress">
              {slideLabels.map((label, index) => (
                <div 
                  key={index} 
                  className={`ai-progress-item ${activeSlide === index ? 'ai-active' : ''}`}
                  onClick={() => setActiveSlide(index)}
                >
                  <div className="ai-progress-icon">
                    {slideIcons[index]}
                  </div>
                  <span className="ai-progress-label">{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Modal Body */}
          <div className="ai-modal-body" ref={modalBodyRef}>
            <div className="ai-modal-content-wrapper">
              {/* Only show image container for slides 0 and 1 */}
              {(activeSlide === 0 || activeSlide === 1) && (
                <div
                  className="ai-modal-image-container"
                  ref={imageRef}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={handleImageClick}
                >
                  {currentImage && (
                    <>
                      {/* Main image */}
                      <img
                        ref={imgRef}
                        src={
                          showOriginal
                            ? (currentImage?.imageUrl || currentImage?.displayImage)
                            : (enhancedPreviewImage || currentImage?.displayImage || currentImage?.imageUrl)
                        }
                        alt="Thumbnail to edit"
                        className="ai-modal-thumbnail"
                        onLoad={e => {
                          const img = e.target;
                          if (img.parentElement) {
                            img.parentElement.style.width = img.naturalWidth + 'px';
                            img.parentElement.style.height = img.naturalHeight + 'px';
                          }
                          setImagePixelWidth(img.naturalWidth);
                        }}
                      />

                      {/* --- BLUR REGIONS FIRST (zIndex: 5) --- */}
                      {blurRegions.map((region) => (
                        <div
                          key={region.id}
                          className="blur-overlay"
                          style={{
                            position: 'absolute',
                            left: `${region.x}%`,
                            top: `${region.y}%`,
                            width: `${region.width}%`,
                            height: `${region.height}%`,
                            transform: 'translate(-50%, -50%)',
                            backdropFilter: `blur(${region.intensity / 10}px)`,
                            WebkitBackdropFilter: `blur(${region.intensity / 10}px)`,
                            backgroundColor: 'rgba(0, 0, 0, 0.2)',
                            borderRadius: '50%',
                            cursor: 'move',
                            zIndex: 5,
                          }}
                          draggable
                          onDragStart={(e) => handleDragStart(e, region.id, 'blur')}
                        >
                          {/* Resizing Handles */}
                          <div
                            className="resize-handle"
                            style={{
                              position: 'absolute',
                              bottom: '-5px',
                              right: '-5px',
                              width: '10px',
                              height: '10px',
                              backgroundColor: 'var(--ios-blue)',
                              cursor: 'nwse-resize',
                              zIndex: 20,
                            }}
                            onMouseDown={(e) => handleResizeStart(e, region.id)}
                          ></div>

                          <button
                            onClick={() => removeBlurRegion(region.id)}
                            style={{
                              position: 'absolute',
                              top: '-10px',
                              right: '-10px',
                              background: 'red',
                              border: 'none',
                              borderRadius: '50%',
                              width: '20px',
                              height: '20px',
                              color: 'white',
                              cursor: 'pointer',
                            }}
                          >
                            ×
                          </button>
                        </div>
                      ))}

                      {/* --- TEXT OVERLAYS (zIndex: 10) --- */}
                      {textElements.map((text) => (
                        <div
                          key={text.id}
                          className="text-overlay"
                          style={{
                            position: 'absolute',
                            left: `${text.x}%`,
                            top: `${text.y}%`,
                            transform: 'translate(-50%, -50%)',
                            color: text.color,
                            fontFamily: text.font,
                            fontSize: `${text.fontSize || 20}px`,
                            cursor: 'move',
                            padding: '4px 8px',
                            backgroundColor: 'rgba(0, 0, 0, 0.5)',
                            borderRadius: '4px',
                            userSelect: 'none',
                            zIndex: 10,
                            maxWidth: '80%',
                            wordBreak: 'break-word',
                          }}
                          draggable
                          onDragStart={(e) => handleDragStart(e, text.id, 'text')}
                        >
                          {text.text}
                          <button
                            onClick={() => removeTextElement(text.id)}
                            style={{
                              marginLeft: '8px',
                              background: 'none',
                              border: 'none',
                              color: 'white',
                              cursor: 'pointer',
                            }}
                          >
                            ×
                          </button>
                          {/* Resizing Handle */}
                          <div
                            className="resize-handle"
                            style={{
                              position: 'absolute',
                              bottom: '-5px',
                              right: '-5px',
                              width: '10px',
                              height: '10px',
                              backgroundColor: 'var(--ios-blue)',
                              cursor: 'nwse-resize',
                              zIndex: 20,
                            }}
                            onMouseDown={(e) => handleTextResizeStart(e, text.id)}
                          ></div>
                        </div>
                      ))}

                      {/* --- LOGO OVERLAY (zIndex: 10) --- */}
                      {/* Logo overlay */}
                        {logoFile && (
                          <div
                            className="logo-overlay"
                            style={{
                              position: 'absolute',
                              left: `${logoPosition.x}%`,
                              top: `${logoPosition.y}%`,
                              transform: 'translate(-50%, -50%)',
                              cursor: 'move',
                              zIndex: 10,
                            }}
                            draggable
                            onDragStart={(e) => handleDragStart(e, 'logo', 'logo')}
                          >
                            <img
                              src={URL.createObjectURL(logoFile)}
                              alt="Logo"
                              style={{
                                width: `${(logoSize / 100) * imagePixelWidth}px`, // Fixed size based on initial imagePixelWidth
                                height: 'auto',
                                maxWidth: 'none', // Prevent scaling based on container
                              }}
                            />
                            <button
                              onClick={removeLogo}
                              style={{
                                position: 'absolute',
                                top: '-10px',
                                right: '-10px',
                                background: 'red',
                                border: 'none',
                                borderRadius: '50%',
                                width: '20px',
                                height: '20px',
                                color: 'white',
                                cursor: 'pointer',
                              }}
                            >
                              ×
                            </button>
                          </div>
                        )}
                      {/* --- BLUR CURSOR INDICATOR --- */}
                      {isAddingBlur && (
                        <div className="blur-cursor-indicator" style={{
                          position: 'absolute',
                          pointerEvents: 'none',
                          left: '50%',
                          top: '50%',
                          transform: 'translate(-50%, -50%)',
                          width: '30px',
                          height: '30px',
                          borderRadius: '50%',
                          backgroundColor: 'rgba(0, 122, 255, 0.3)',
                          border: '2px dashed var(--ios-blue)',
                          zIndex: 20
                        }} />
                      )}
                    </>
                  )}
                </div>
              )}

              <div className="ai-modal-controls">
                {/* Remove "Compare with original" toggle for the last slide */}
                {activeSlide !== 2 && (
                  <div className="compare-toggle">
                    <FormControlLabel
                      control={
                        <Switch
                          checked={showOriginal}
                          onChange={() => setShowOriginal(!showOriginal)}
                          color="primary"
                        />
                      }
                      label="Compare with original"
                    />
                  </div>
                )}

                {/* Slide 0: Text & Logo Edit */}
                {activeSlide === 0 && (
                  <div className="ai-slide ai-prompt-slide">
                    <div className="text-edit-controls">
                      <FormControl 
                        fullWidth 
                        sx={{ 
                          mb: 2,
                          '& .MuiOutlinedInput-root': {
                            borderRadius: '12px',
                            backgroundColor: 'var(--input-bg)',
                            '&:hover .MuiOutlinedInput-notchedOutline': {
                              borderColor: 'var(--ios-blue)',
                            },
                            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                              borderColor: 'var(--ios-blue)',
                              borderWidth: '2px',
                            }
                          },
                          '& .MuiInputLabel-root': {
                            color: 'var(--text-secondary)',
                          },
                          '& .MuiInputLabel-root.Mui-focused': {
                            color: 'var(--ios-blue)',
                          },
                          '& .MuiSelect-select': {
                            padding: '10px 14px',
                            color: 'var(--text-primary)',
                          },
                          '& .MuiSvgIcon-root': {
                            color: 'var(--text-secondary)',
                          }
                        }} 
                        size="small"
                      >
                        <InputLabel>Language</InputLabel>
                        <Select
                          value={language}
                          onChange={(e) => {
                            // Only allow English, show toast for others
                            if (e.target.value === 'english') {
                              setLanguage('english');
                            } else {
                              setToastOpen(true);
                            }
                          }}
                          label="Language"
                          MenuProps={{
                            PaperProps: {
                              sx: {
                                backgroundColor: 'var(--modal-bg)',
                                color: 'var(--text-primary)',
                              }
                            }
                          }}
                        >
                          {allLanguages.map(lang => (
                            <MenuItem
                              key={lang.code}
                              value={lang.code}
                              sx={{
                                color: lang.enabled ? 'var(--text-primary)' : 'var(--text-secondary)',
                                opacity: lang.enabled ? 1 : 0.5,
                                pointerEvents: lang.enabled ? 'auto' : 'auto', // allow pointer events for all
                              }}
                            >
                              {lang.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>

                      <TextField
                        fullWidth
                        label="Enter text to add"
                        variant="outlined"
                        value={currentText}
                        onChange={(e) => setCurrentText(e.target.value)}
                        sx={{ 
                          mb: 2,
                          '& .MuiOutlinedInput-root': {
                            borderRadius: '12px',
                            backgroundColor: 'var(--input-bg)',
                            '&:hover .MuiOutlinedInput-notchedOutline': {
                              borderColor: 'var(--ios-blue)',
                            },
                            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                              borderColor: 'var(--ios-blue)',
                              borderWidth: '2px',
                            }
                          },
                          '& .MuiInputLabel-root': {
                            color: 'var(--text-secondary)',
                          },
                          '& .MuiInputLabel-root.Mui-focused': {
                            color: 'var(--ios-blue)',
                          },
                          '& .MuiOutlinedInput-input': {
                            padding: '10px 14px',
                            color: 'var(--text-primary)',
                          }
                        }}
                        size="small"
                      />

                      <div className="text-style-controls">
                        <FormControl 
                          sx={{ 
                            minWidth: 120, 
                            mr: 2,
                            mb: 2,  // Added margin bottom for spacing
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '12px',
                              backgroundColor: 'var(--input-bg)',
                              '&:hover .MuiOutlinedInput-notchedOutline': {
                                borderColor: 'var(--ios-blue)',
                              },
                            },
                            '& .MuiInputLabel-root': {
                              color: 'var(--text-secondary)',
                            },
                            '& .MuiSelect-select': {
                              padding: '10px 14px',
                              color: 'var(--text-primary)',
                            },
                            '& .MuiSvgIcon-root': {
                              color: 'var(--text-secondary)',
                            },
                            '& .MuiPaper-root': {
                              backgroundColor: 'var(--modal-bg)',
                              color: 'var(--text-primary)',
                              borderRadius: '12px',
                              marginTop: '8px',
                              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                            },
                            '& .MuiList-root': {
                              padding: '8px 0',
                            },
                            '& .MuiMenuItem-root': {
                              '&:hover': {
                                backgroundColor: 'var(--button-outline-hover)',
                              },
                              '&.Mui-selected': {
                                backgroundColor: 'var(--ios-blue)',
                                color: 'white',
                                '&:hover': {
                                  backgroundColor: 'var(--ios-blue-hover)',
                                }
                              }
                            }
                          }} 
                          size="small"
                        >
                          <InputLabel>Font</InputLabel>
                          <Select
                            value={font}
                            onChange={(e) => setFont(e.target.value)}
                            label="Font"
                            MenuProps={{
                              PaperProps: {
                                sx: {
                                  backgroundColor: 'var(--modal-bg)',
                                  color: 'var(--text-primary)',
                                  '& .MuiMenuItem-root': {
                                    color: 'var(--text-primary)',
                                    '&:hover': {
                                      backgroundColor: 'var(--button-outline-hover)',
                                    }
                                  }
                                }
                              }
                            }}
                          >
                            {fonts.map((f) => (
                              <MenuItem 
                                key={f} 
                                value={f}
                                sx={{
                                  color: 'var(--text-primary)',
                                  '&:hover': {
                                    backgroundColor: 'var(--button-outline-hover)',
                                  }
                                }}
                              >
                                {f}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>

                        <FormControl 
                          sx={{ 
                            minWidth: 120, 
                            mr: 2,
                            mb: 2,  // Added margin bottom for spacing
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '12px',
                              backgroundColor: 'var(--input-bg)',
                              '&:hover .MuiOutlinedInput-notchedOutline': {
                                borderColor: 'var(--ios-blue)',
                              },
                            },
                            '& .MuiInputLabel-root': {
                              color: 'var(--text-secondary)',
                            },
                            '& .MuiSelect-select': {
                              padding: '10px 14px',
                              color: 'var(--text-primary)',
                            },
                            '& .MuiSvgIcon-root': {
                              color: 'var(--text-secondary)',
                            },
                            '& .MuiPaper-root': {
                              backgroundColor: 'var(--modal-bg)',
                              color: 'var(--text-primary)',
                              borderRadius: '12px',
                              marginTop: '8px',
                              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                            }
                          }} 
                          size="small"
                        >
                          <InputLabel>Color</InputLabel>
                          <Select
                            value={textColor}
                            onChange={(e) => setTextColor(e.target.value)}
                            label="Color"
                            MenuProps={{
                              PaperProps: {
                                sx: {
                                  backgroundColor: 'var(--modal-bg)',
                                  color: 'var(--text-primary)',
                                  '& .MuiMenuItem-root': {
                                    color: 'var(--text-primary)',
                                    '&:hover': {
                                      backgroundColor: 'var(--button-outline-hover)',
                                    }
                                  }
                                }
                              }
                            }}
                          >
                            {colors.map((c) => (
                              <MenuItem 
                                key={c} 
                                value={c}
                                sx={{
                                  color: 'var(--text-primary)',
                                  '&:hover': {
                                    backgroundColor: 'var(--button-outline-hover)',
                                  }
                                }}
                              >
                                <div style={{ display: 'flex', alignItems: 'center' }}>
                                  <div style={{
                                    width: '20px',
                                    height: '20px',
                                    backgroundColor: c,
                                    marginRight: '8px',
                                    border: '1px solid var(--text-secondary)',
                                    borderRadius: '4px'
                                  }} />
                                  {c}
                                </div>
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>

                        <FormControl 
                          sx={{ 
                            minWidth: 120,
                            mb: 2,  // Added margin bottom for spacing
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '12px',
                              backgroundColor: 'var(--input-bg)',
                              '&:hover .MuiOutlinedInput-notchedOutline': {
                                borderColor: 'var(--ios-blue)',
                              },
                            },
                            '& .MuiInputLabel-root': {
                              color: 'var(--text-secondary)',
                            },
                            '& .MuiSelect-select': {
                              padding: '10px 14px',
                              color: 'var(--text-primary)',
                            },
                            '& .MuiSvgIcon-root': {
                              color: 'var(--text-secondary)',
                            },
                            '& .MuiPaper-root': {
                              backgroundColor: 'var(--modal-bg)',
                              color: 'var(--text-primary)',
                              borderRadius: '12px',
                              marginTop: '8px',
                              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                            }
                          }} 
                          size="small"
                        >
                          <InputLabel>Position</InputLabel>
                          <Select
                            value={textPosition}
                            onChange={(e) => setTextPosition(e.target.value)}
                            label="Position"
                            MenuProps={{
                              PaperProps: {
                                sx: {
                                  backgroundColor: 'var(--modal-bg)',
                                  color: 'var(--text-primary)',
                                  '& .MuiMenuItem-root': {
                                    color: 'var(--text-primary)',
                                    '&:hover': {
                                      backgroundColor: 'var(--button-outline-hover)',
                                    }
                                  }
                                }
                              }
                            }}
                          >
                            {positions.map((p) => (
                              <MenuItem 
                                key={p} 
                                value={p}
                                sx={{
                                  color: 'var(--text-primary)',
                                  '&:hover': {
                                    backgroundColor: 'var(--button-outline-hover)',
                                  }
                                }}
                              >
                                {p.replace('-', ' ')}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </div>

                      <Button
                        variant="contained"
                        onClick={addTextElement}
                        sx={{ 
                          mt: 2, 
                          mb: 2,
                          borderRadius: '12px',
                          backgroundColor: 'var(--ios-blue)',
                          padding: '8px 16px',
                          textTransform: 'none',
                          fontWeight: 500,
                          boxShadow: '0 2px 8px rgba(0, 122, 255, 0.25)',
                          '&:hover': {
                            backgroundColor: 'var(--ios-blue-hover)',
                            boxShadow: '0 4px 12px rgba(0, 122, 255, 0.35)',
                          },
                          '&:disabled': {
                            backgroundColor: 'rgba(94, 98, 102, 0.5)',
                            color: 'white'
                          }
                        }}
                        disabled={!currentText.trim()}
                        fullWidth
                      >
                        Add Text
                      </Button>

                      <div className="logo-upload">
                        <input
                          accept="image/*"
                          id="logo-upload"
                          type="file"
                          style={{ display: 'none' }}
                          onChange={handleLogoUpload}
                        />
                        <label htmlFor="logo-upload">
                          <Button 
                            variant="contained" 
                            component="span" 
                            fullWidth
                            sx={{ 
                              borderRadius: '12px',
                              backgroundColor: 'var(--ios-blue)',
                              padding: '8px 16px',
                              textTransform: 'none',
                              fontWeight: 500,
                              boxShadow: '0 2px 8px rgba(0, 122, 255, 0.25)',
                              '&:hover': {
                                backgroundColor: 'var(--ios-blue-hover)',
                                boxShadow: '0 4px 12px rgba(0, 122, 255, 0.35)',
                              }
                            }}
                          >
                            Upload Logo
                          </Button>
                        </label>
                      </div>

                      {/* {logoFile && (
                        <div className="logo-size-control">
                          <label className="ai-slider-label">Logo Size</label>
                          <Slider
                            value={logoSize}
                            onChange={(_, value) => setLogoSize(value)}
                            min={10}
                            max={200}
                            sx={{ 
                              color: 'var(--ios-blue)',
                              '& .MuiSlider-thumb': {
                                width: 18,
                                height: 18,
                                backgroundColor: 'var(--ios-blue)'
                              },
                              '& .MuiSlider-rail': {
                                backgroundColor: 'rgba(0, 122, 255, 0.2)',
                              }
                            }}
                          />
                          <span className="ai-slider-value">{logoSize}%</span>
                        </div>
                      )} */}

                      {logoFile && (
                        <div className="logo-size-control">
                          <label className="ai-slider-label">Logo Size</label>
                          <Slider
                            value={logoSize}
                            onChange={(_, value) => setLogoSize(value)}
                            min={2} // allow scaling down to 2%
                            max={200}
                            sx={{ 
                              color: 'var(--ios-blue)',
                              '& .MuiSlider-thumb': {
                                width: 18,
                                height: 18,
                                backgroundColor: 'var(--ios-blue)'
                              },
                              '& .MuiSlider-rail': {
                                backgroundColor: 'rgba(0, 122, 255, 0.2)',
                              }
                            }}
                          />
                          <span className="ai-slider-value">
                            {Math.round(Math.max(10, logoSize))}%
                          </span>
                        </div>
                      )}

                      <div className="blur-controls">
                        <Button
                          variant={isAddingBlur ? "contained" : "outlined"}
                          onClick={toggleBlurMode}
                          startIcon={<BlurOnIcon />}
                          sx={{ 
                            mt: 2,
                            mb: 2,
                            borderRadius: '12px',
                            backgroundColor: isAddingBlur ? 'var(--ios-blue)' : 'transparent',
                            borderColor: 'var(--ios-blue)',
                            color: isAddingBlur ? 'white' : 'var(--ios-blue)',
                            padding: '8px 16px',
                            textTransform: 'none',
                            fontWeight: 500,
                            boxShadow: isAddingBlur ? '0 2px 8px rgba(0, 122, 255, 0.25)' : 'none',
                            '&:hover': {
                              backgroundColor: isAddingBlur ? 'var(--ios-blue-hover)' : 'var(--button-outline-hover)',
                              boxShadow: isAddingBlur ? '0 4px 12px rgba(0, 122, 255, 0.35)' : 'none',
                            }
                          }}
                          fullWidth
                        >
                          {isAddingBlur ? 'Click on image to add blur' : 'Add Blur Region'}
                        </Button>

                        {/* Add this just before the error message */}
                        <Button
                          variant="outlined"
                          onClick={resetTextLogoSlide}
                          sx={{ 
                            mt: 2,
                            borderRadius: '12px',
                            borderColor: 'var(--ios-red)',
                            color: 'var(--ios-red)',
                            padding: '8px 16px',
                            textTransform: 'none',
                            fontWeight: 500,
                            '&:hover': {
                              backgroundColor: 'rgba(255, 59, 48, 0.1)',
                              borderColor: 'var(--ios-red)',
                            }
                          }}
                          fullWidth
                        >
                          Reset All Changes
                        </Button>

                        {blurRegions.length > 0 && (
                          <div className="blur-intensity-control">
                            <label className="ai-slider-label">Blur Intensity</label>
                            <Slider
                              value={blurIntensity}
                              onChange={(_, value) => {
                                setBlurIntensity(value);
                                setBlurRegions(prev =>
                                  prev.map(region => ({
                                    ...region,
                                    intensity: value
                                  }))
                                );
                              }}
                              min={10}
                              max={100}
                              sx={{
                                color: 'var(--ios-blue)',
                                '& .MuiSlider-thumb': {
                                  width: 18,
                                  height: 18,
                                  backgroundColor: 'var(--ios-blue)'
                                },
                                '& .MuiSlider-rail': {
                                  backgroundColor: 'rgba(0, 122, 255, 0.2)',
                                }
                              }}
                            />
                            <span className="ai-slider-value">{blurIntensity}%</span>
                          </div>
                        )}
                      </div>

                      {error && <p className="ai-error-message">{error}</p>}
                    </div>
                  </div>
                )}

                {/* Slide 1: Manual Edit */}
                {activeSlide === 1 && (
                  <div className="ai-slide ai-manual-slide">
                    <div className="ai-slider-container">
                      <FormControl 
                        fullWidth 
                        sx={{ 
                          mb: 2,
                          '& .MuiOutlinedInput-root': {
                            borderRadius: '12px',
                            backgroundColor: 'var(--input-bg)',
                            '&:hover .MuiOutlinedInput-notchedOutline': {
                              borderColor: 'var(--ios-blue)',
                            },
                            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                              borderColor: 'var(--ios-blue)',
                              borderWidth: '2px',
                            }
                          },
                          '& .MuiInputLabel-root': {
                            color: 'var(--text-secondary)',
                          },
                          '& .MuiInputLabel-root.Mui-focused': {
                            color: 'var(--ios-blue)',
                          },
                          '& .MuiSelect-select': {
                            padding: '10px 14px',
                            color: 'var(--text-primary)',
                          },
                          '& .MuiSvgIcon-root': {
                            color: 'var(--text-secondary)',
                          }
                        }} 
                        size="small"
                      >
                        <InputLabel>Aspect Ratio</InputLabel>
                        <Select
                          value={manualEditSettings.aspectRatio}
                          onChange={(e) => handleSettingChange('aspectRatio', e.target.value)}
                          label="Aspect Ratio"
                          startAdornment={<AspectRatioIcon sx={{ color: 'var(--text-secondary)', mr: 1 }} />}
                        >
                          {aspectRatios.map((ratio) => (
                            <MenuItem key={ratio} value={ratio === 'Original' ? '' : ratio}>
                              {ratio}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>

                      <div className="ai-slider-group">
                        <label className="ai-slider-label">Brightness</label>
                        <Slider
                          value={manualEditSettings.brightness}
                          onChange={(_, value) => handleSettingChange('brightness', value)}
                          min={0}
                          max={100}
                          sx={{ 
                            color: 'var(--ios-blue)',
                            '& .MuiSlider-thumb': {
                              width: 18,
                              height: 18,
                              backgroundColor: 'var(--ios-blue)'
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(0, 122, 255, 0.2)',
                            }
                          }}
                        />
                        <span className="ai-slider-value">{manualEditSettings.brightness}%</span>
                      </div>
                      
                      <div className="ai-slider-group">
                        <label className="ai-slider-label">Contrast</label>
                        <Slider
                          value={manualEditSettings.contrast}
                          onChange={(_, value) => handleSettingChange('contrast', value)}
                          min={0}
                          max={100}
                          sx={{ 
                            color: 'var(--ios-blue)',
                            '& .MuiSlider-thumb': {
                              width: 18,
                              height: 18,
                              backgroundColor: 'var(--ios-blue)'
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(0, 122, 255, 0.2)',
                            }
                          }}
                        />
                        <span className="ai-slider-value">{manualEditSettings.contrast}%</span>
                      </div>
                      
                      <div className="ai-slider-group">
                        <label className="ai-slider-label">Saturation</label>
                        <Slider
                          value={manualEditSettings.saturation}
                          onChange={(_, value) => handleSettingChange('saturation', value)}
                          min={0}
                          max={100}
                          sx={{ 
                            color: 'var(--ios-blue)',
                            '& .MuiSlider-thumb': {
                              width: 18,
                              height: 18,
                              backgroundColor: 'var(--ios-blue)'
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(0, 122, 255, 0.2)',
                            }
                          }}
                        />
                        <span className="ai-slider-value">{manualEditSettings.saturation}%</span>
                      </div>
                      
                      <div className="ai-slider-group">
                        <label className="ai-slider-label">Hue</label>
                        <Slider
                          value={manualEditSettings.hue}
                          onChange={(_, value) => handleSettingChange('hue', value)}
                          min={-180}
                          max={180}
                          sx={{ 
                            color: 'var(--ios-blue)',
                            '& .MuiSlider-thumb': {
                              width: 18,
                              height: 18,
                              backgroundColor: 'var(--ios-blue)'
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(0, 122, 255, 0.2)',
                            }
                          }}
                        />
                        <span className="ai-slider-value">{manualEditSettings.hue}°</span>
                      </div>
                      
                      <div className="ai-slider-group">
                        <label className="ai-slider-label">Sharpness</label>
                        <Slider
                          value={manualEditSettings.sharpness}
                          onChange={(_, value) => handleSettingChange('sharpness', value)}
                          min={0}
                          max={100}
                          sx={{ 
                            color: 'var(--ios-blue)',
                            '& .MuiSlider-thumb': {
                              width: 18,
                              height: 18,
                              backgroundColor: 'var(--ios-blue)'
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(0, 122, 255, 0.2)',
                            }
                          }}
                        />
                        <span className="ai-slider-value">{manualEditSettings.sharpness}%</span>
                      </div>

                      <div className="toggle-controls">
                        {/* HDR Toggle */}
                        <FormControlLabel
                          control={
                            <Switch
                              checked={manualEditSettings.hdr}
                              onChange={(e) => handleSettingChange('hdr', e.target.checked)}
                              color="primary"
                              sx={{
                                '& .MuiSwitch-switchBase.Mui-checked': {
                                  color: 'var(--ios-blue)',
                                },
                                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                                  backgroundColor: 'var(--ios-blue)',
                                }
                              }}
                            />
                          }
                          label="HDR"
                          sx={{ color: 'var(--text-primary)' }}
                        />

                        {/* Beautify Toggle */}
                        <FormControlLabel
                          control={
                            <Switch
                              checked={manualEditSettings.beautify}
                              onChange={(e) => handleSettingChange('beautify', e.target.checked)}
                              color="primary"
                              sx={{
                                '& .MuiSwitch-switchBase.Mui-checked': {
                                  color: 'var(--ios-blue)',
                                },
                                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                                  backgroundColor: 'var(--ios-blue)',
                                }
                              }}
                            />
                          }
                          label="Beautify"
                          sx={{ color: 'var(--text-primary)' }}
                        />
                      </div>
                        <Button
                          variant="outlined"
                          onClick={resetManualEditSlide}
                          sx={{ 
                            mt: 2,
                            borderRadius: '12px',
                            borderColor: 'var(--ios-red)',
                            color: 'var(--ios-red)',
                            padding: '8px 16px',
                            textTransform: 'none',
                            fontWeight: 500,
                            '&:hover': {
                              backgroundColor: 'rgba(255, 59, 48, 0.1)',
                              borderColor: 'var(--ios-red)',
                            }
                          }}
                          fullWidth
                        >
                          Reset All Adjustments
                        </Button>
                    </div>
                    {error && <p className="ai-error-message">{error}</p>}
                  </div>
                )}

                {/* Slide 2: AI Enhancement */}
                {activeSlide === 2 && (
                  <div
                    className="ai-slide ai-ai-enhancement-slide"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '100%',
                      minHeight: 400,
                      textAlign: 'center',
                    }}
                  >
                    
                    <div
                      className="ai-enhancement-options"
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textAlign: 'center',
                        width: '100%',
                      }}
                    >
                      <h3 className="ai-enhancement-title" style={{ marginBottom: 8 }}>AI Enhancement</h3>
                      <p className="ai-enhancement-description" style={{ marginBottom: 24 }}>
                        Let our AI automatically enhance your thumbnail with professional quality
                      </p>
                      <div className="enhancement-features" style={{ width: '100%', maxWidth: 500 }}>
                        <div className="feature-item" style={{ marginBottom: 16 }}>
                          <h4 style={{ margin: 0 }}>Auto Color Correction</h4>
                          <p style={{ margin: 0 }}>Automatically adjust colors for optimal appearance</p>
                        </div>
                        <div className="feature-item" style={{ marginBottom: 16 }}>
                          <h4 style={{ margin: 0 }}>Noise Reduction</h4>
                          <p style={{ margin: 0 }}>Reduce graininess and improve clarity</p>
                        </div>
                        <div className="feature-item" style={{ marginBottom: 16 }}>
                          <h4 style={{ margin: 0 }}>Smart Sharpening</h4>
                          <p style={{ margin: 0 }}>Enhance details without artifacts</p>
                        </div>
                        <div className="feature-item" style={{ marginBottom: 16 }}>
                          <h4 style={{ margin: 0 }}>Face Enhancement</h4>
                          <p style={{ margin: 0 }}>Improve facial features naturally</p>
                        </div>
                      </div>
                      <p
                        className="ai-enhancement-disclaimer"
                        style={{
                          color: 'red',
                          fontWeight: 'bold',
                          backgroundColor: 'rgba(255, 235, 235, 0.8)',
                          padding: '10px',
                          borderRadius: '8px',
                          marginTop: '20px',
                          maxWidth: 500,
                          position: 'relative',
                          textAlign: 'center',
                        }}
                      >
                        *Disclaimer: All these options will only be allowed in the production environment. Please ensure you are in the correct environment before proceeding.
                      </p>
                    </div>
                  </div>
                )}
            </div>
            </div>
          </div>

          {/* Modal Footer */}
          <div className="ai-modal-actions">
            <div className="ai-modal-navigation">
              <Button
                variant="outlined"
                onClick={handlePrevSlide}
                disabled={activeSlide === 0 || isProcessing}
                startIcon={<ArrowBackIosIcon />}
                sx={{ 
                  color: 'var(--ios-blue)',
                  borderColor: 'var(--ios-blue)',
                  '&:hover': { 
                    backgroundColor: 'var(--button-outline-hover)',
                    borderColor: 'var(--ios-blue)'
                  },
                  visibility: activeSlide === 0 ? 'hidden' : 'visible'
                }}
              >
                Back
              </Button>
              
              <Button
                variant="outlined"
                onClick={handleNextSlide}
                disabled={activeSlide === 2 || isProcessing}
                endIcon={<ArrowForwardIosIcon />}
                sx={{ 
                  color: 'var(--ios-blue)',
                  borderColor: 'var(--ios-blue)',
                  '&:hover': { 
                    backgroundColor: 'var(--button-outline-hover)',
                    borderColor: 'var(--ios-blue)'
                  },
                  visibility: activeSlide === 2 ? 'hidden' : 'visible'
                }}
              >
                Next
              </Button>
            </div>
            
            <div className="ai-modal-buttons">
              <Button
                variant="outlined"
                onClick={handleDownload}
                disabled={isProcessing}
                sx={{ 
                  mr: 2,
                  color: 'var(--ios-blue)',
                  borderColor: 'var(--ios-blue)',
                  '&:hover': { 
                    backgroundColor: 'var(--button-outline-hover)',
                    borderColor: 'var(--ios-blue)'
                  }
                }}
              >
                Download
              </Button>

            {/* New Upscale and Download Button */}
            <Button
              variant="outlined"
              onClick={handleUpscaleAndDownload}
              disabled={isProcessing}
              sx={{ 
                mr: 2,
                color: 'var(--ios-blue)',
                borderColor: 'var(--ios-blue)',
                '&:hover': { 
                  backgroundColor: 'var(--button-outline-hover)',
                  borderColor: 'var(--ios-blue)'
                }
              }}
            >
              {isProcessing ? (
                <>
                  <CircularProgress size={24} sx={{ color: 'var(--ios-blue)', mr: 1 }} />
                  Upscaling...
                </>
              ) : 'Upscale and Download'}
            </Button>

            {error && (
              <div style={{ color: 'red', marginTop: '10px' }}>
                Error: {error}
                <br />
                <button 
                  onClick={() => setError(null)}
                  style={{ 
                    background: 'none', 
                    border: 'none', 
                    color: 'var(--ios-blue)', 
                    cursor: 'pointer',
                    marginTop: '5px'
                  }}
                >
                  Dismiss
                </button>
              </div>
            )}

              <Button
                variant="outlined"
                onClick={handleCloseModal}
                disabled={isProcessing}
                sx={{ 
                  mr: 2,
                  color: 'var(--ios-blue)',
                  borderColor: 'var(--ios-blue)',
                  '&:hover': { 
                    backgroundColor: 'var(--button-outline-hover)',
                    borderColor: 'var(--ios-blue)'
                  }
                }}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                onClick={handleApplyEdit}
                disabled={isProcessing || (activeSlide === 0 && textElements.length === 0 && !logoFile && blurRegions.length === 0)}
                sx={{
                  backgroundColor: 'var(--ios-blue)',
                  '&:hover': {
                    backgroundColor: 'var(--ios-blue-hover)'
                  }
                }}
              >
                {isProcessing ? (
                  <>
                    <CircularProgress size={24} sx={{ color: 'white', mr: 1 }} />
                    Applying...
                  </>
                ) : 'Apply Edit'}
              </Button>
            </div>
          </div>
        </div>
      </Modal>

      <Modal
        open={previewModalOpen}
        onClose={() => setPreviewModalOpen(false)}
        aria-labelledby="preview-modal-title"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'auto'
        }}
      >
        <div style={{
          background: 'var(--modal-bg)', // Use theme variable
          color: 'var(--text-primary)',  // Use theme variable
          borderRadius: 12,
          padding: 24,
          maxWidth: 600,
          boxShadow: '0 4px 24px rgba(0,0,0,0.18)'
        }}>
          <h2 id="preview-modal-title" style={{ color: 'var(--text-primary)' }}>Preview Edited Image</h2>
          {previewImage && (
            <img
              src={previewImage}
              alt="Preview"
              style={{ maxWidth: '100%', borderRadius: 8, marginTop: 16 }}
            />
          )}
          <Button
            variant="outlined"
            onClick={() => setPreviewModalOpen(false)}
            sx={{ 
              mt: 2,
              color: 'var(--ios-blue)',
              borderColor: 'var(--ios-blue)',
              '&:hover': { 
                backgroundColor: 'var(--button-outline-hover)',
                borderColor: 'var(--ios-blue)'
              }
            }}
          >
            Close
          </Button>
        </div>
      </Modal>

      <Snackbar
        open={toastOpen}
        autoHideDuration={2500}
        onClose={handleToastClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <MuiAlert onClose={handleToastClose} severity="info" sx={{ width: '100%' }}>
          This feature will be available after production launch!
        </MuiAlert>
      </Snackbar>
    </div>
  );
};

export default AIEditScreen;