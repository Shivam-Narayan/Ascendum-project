import API_BASE_URL from "../config";

// const generateThumbnails = async (requestData) => {
//   try {

//     const token = localStorage.getItem('token');
//     console.log("Using token:", token);
//     const userEmail = localStorage.getItem('userEmail');
//     console.log("Using emial:", userEmail);
    
//     if (!token || !userEmail) {
//       throw new Error("No authentication token or user data found. Please login again.");
//     }

//     const userSpecificRequest = {
//       ...requestData,
//       user_email: userEmail
//     };
    
//     const response = await fetch(`${API_BASE_URL}accounts/generate-thumbnails/`, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         "Authorization": `Bearer ${token}`
//       },
//       body: JSON.stringify(userSpecificRequest),
//     });

//     if (!response.ok) {
//       throw new Error("Failed to generate thumbnails");
//     }

//     const data = await response.json();
    
//     if (!data.success) {
//       throw new Error("Failed to generate thumbnails");
//     }

//     // Helper function to construct proper URLs
//     const constructUrl = (url) => {
//       if (!url) return '';
//       // If URL is already absolute, return as-is
//       if (url.startsWith('http://') || url.startsWith('https://')) {
//         return url;
//       }
//       // Otherwise, combine with base URL
//       return `${API_BASE_URL}${url.replace(/^\//, '')}`;
//     };

//     return {
//       thumbnails: data.thumbnails.map((thumbnail) => ({
//         id: thumbnail.timestamp,
//         imageUrl: constructUrl(thumbnail.original.url),
//         enhancedImageUrl: constructUrl(thumbnail.enhanced?.url),
//         timestamp: thumbnail.timestamp,
//         emotion: thumbnail.dominant_emotion || 'No emotion detected',
//         faceCoverage: thumbnail.face_coverage.toFixed(2),
//       })),
//       videoInfo: {
//         title: data.video_title,
//         thumbnail: data.original_thumbnail,
//         duration: `${Math.floor(data.stats.total_frames / 30)}s`,
//       }
//     };
//   } catch (error) {
//     console.error("API Error:", error);
//     throw error;
//   }
// };

// const generateThumbnails = async (requestData) => {
//   try {
//     const token = localStorage.getItem('token');
//     const userEmail = localStorage.getItem('userEmail');
    
//     if (!token || !userEmail) {
//       throw new Error("No authentication token or user data found. Please login again.");
//     }

//     const userSpecificRequest = {
//       ...requestData,
//       user_email: userEmail
//     };
    
//     // For regular API call (fallback)
//     const response = await fetch(`${API_BASE_URL}accounts/generate-thumbnails/`, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         "Authorization": `Bearer ${token}`
//       },
//       body: JSON.stringify(userSpecificRequest),
//     });

//     if (!response.ok) {
//       throw new Error("Failed to generate thumbnails");
//     }

//     const data = await response.json();
    
//     if (!data.success) {
//       throw new Error("Failed to generate thumbnails");
//     }

//     // Helper function to construct proper URLs
//     const constructUrl = (url) => {
//       if (!url) return '';
//       if (url.startsWith('http://') || url.startsWith('https://')) {
//         return url;
//       }
//       return `${API_BASE_URL}${url.replace(/^\//, '')}`;
//     };

//     return {
//       thumbnails: data.thumbnails.map((thumbnail) => ({
//         id: thumbnail.timestamp,
//         imageUrl: constructUrl(thumbnail.original.url),
//         enhancedImageUrl: constructUrl(thumbnail.enhanced?.url),
//         timestamp: thumbnail.timestamp,
//         emotion: thumbnail.dominant_emotion || 'No emotion detected',
//         faceCoverage: thumbnail.face_coverage.toFixed(2),
//       })),
//       videoInfo: {
//         title: data.video_title,
//         thumbnail: data.original_thumbnail,
//         duration: `${Math.floor(data.stats.total_frames / 30)}s`,
//       },
//       stats: data.stats
//     };
//   } catch (error) {
//     console.error("API Error:", error);
//     throw error;
//   }
// };

const generateThumbnails = async (requestData) => {
  try {
    const token = localStorage.getItem('token');
    const userEmail = localStorage.getItem('userEmail');
    
    if (!token || !userEmail) {
      throw new Error("No authentication token or user data found. Please login again.");
    }

    const userSpecificRequest = {
      ...requestData,
      user_email: userEmail
    };
    
    const response = await fetch(`${API_BASE_URL}accounts/generate-thumbnails/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(userSpecificRequest),
    });

    if (!response.ok) {
      throw new Error("Failed to generate thumbnails");
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error("Failed to generate thumbnails");
    }

    // Helper function to construct proper URLs
    const constructUrl = (url) => {
      if (!url) return '';
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
      }
      return `${API_BASE_URL}${url.replace(/^\//, '')}`;
    };

    return {
      thumbnails: data.thumbnails.map((thumbnail) => ({
        id: thumbnail.timestamp,
        imageUrl: constructUrl(thumbnail.original.url),
        enhancedImageUrl: constructUrl(thumbnail.enhanced?.url),
        timestamp: thumbnail.timestamp,
        emotion: thumbnail.dominant_emotion || 'No emotion detected',
        faceCoverage: thumbnail.face_coverage.toFixed(2),
      })),
      videoInfo: {
        title: data.video_title,
        thumbnail: data.original_thumbnail,
        duration: `${Math.floor(data.stats.total_frames / 30)}s`,
      },
      stats: data.stats
    };
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

export default generateThumbnails;