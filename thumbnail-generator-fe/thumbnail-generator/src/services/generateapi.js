import API_BASE_URL from "../config";

const constructUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  return `${API_BASE_URL}${url.replace(/^\//, '')}`;
};

const generateThumbnailsFromFile = async (formData) => {
  try {
    const token = localStorage.getItem('token');
    const userEmail = localStorage.getItem('userEmail');
    if (!token || !userEmail) {
      throw new Error("No authentication token or user data found. Please login again.");
    }

    formData.append('user_email', userEmail);

    const response = await fetch(`${API_BASE_URL}accounts/generate-thumbnails/`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to generate thumbnails");
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error("Failed to generate thumbnails");
    }

    return {
      thumbnails: data.thumbnails.map((thumbnail) => ({
        id: thumbnail.timestamp,
        imageUrl: constructUrl(thumbnail.original.url),
        enhancedImageUrl: constructUrl(thumbnail.enhanced?.url),
        timestamp: thumbnail.timestamp,
        emotion: thumbnail.dominant_emotion || 'No emotion detected',
        faceCoverage: thumbnail.face_coverage?.toFixed(2) ?? '',
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

export default generateThumbnailsFromFile;