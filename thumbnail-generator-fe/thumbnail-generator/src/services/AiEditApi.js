import API_BASE_URL from '../config';

export const enhanceThumbnails = async (thumbnails, enhancementParams) => {
  try {
    const formData = new FormData();

    // Add thumbnails data
    formData.append('thumbnails', JSON.stringify(thumbnails));

    // Add enhancement parameters
    for (const key in enhancementParams) {
      if (key === 'logo_file' && enhancementParams[key]) {
        // Handle file upload
        formData.append('logo_file', enhancementParams[key]);
      } else {
        formData.append(key, enhancementParams[key]);
      }
    }

    const response = await fetch(`${API_BASE_URL}api/enhance-thumbnails/`, {
      method: 'POST',
      body: formData,
      headers: {
        // DO NOT set Content-Type when sending FormData with fetch — the browser will set it correctly
        // 'Content-Type': 'multipart/form-data' — omit this line!
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData?.message || 'Failed to enhance thumbnails');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error enhancing thumbnails:', error);
    throw error;
  }
};
