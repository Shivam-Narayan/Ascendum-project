import API_BASE_URL from '../config';

const upscaleImage = async (thumbnailUrl, token) => {
  const formData = new FormData();
  formData.append('thumbnail_url', thumbnailUrl);

  try {
    console.log('Sending upscale request for:', thumbnailUrl);
    
    const response = await fetch(`${API_BASE_URL}accounts/singleUpscale/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    // First check if the response is JSON (error case)
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const errorData = await response.json();
      console.error('Server returned error:', errorData);
      throw new Error(errorData.error || 'Failed to upscale image');
    }

    // If not JSON, it should be an image
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Create a blob from the response
    const blob = await response.blob();

    // Verify it's actually an image
    if (!blob.type.startsWith('image/')) {
      throw new Error('Server did not return an image');
    }

    // Create a temporary link to download the file
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `upscaled_${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);

    return true;
  } catch (error) {
    console.error('Error in upscaleImage:', error);
    throw error;
  }
};

export default upscaleImage;