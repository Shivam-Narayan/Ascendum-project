import API_BASE_URL from "../config";

export const uploadImagesForDetection = async (token, imageFiles) => {
  const formData = new FormData();
  
  // Append each image to the form data
  for (let i = 0; i < imageFiles.length; i++) {
    formData.append('image', imageFiles[i]);
  }

  try {
    const response = await fetch(`${API_BASE_URL}seamguard/detection/image/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading images for detection:', error);
    throw error;
  }
};

export const getDefectDetails = async (token, batchId) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/detection/defect/image?batch_id=${batchId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching defect details:', error);
    throw error;
  }
};

export const uploadVideoForDetection = async (token, videoFile) => {
  const formData = new FormData();
  formData.append('video', videoFile);

  try {
    const response = await fetch(`${API_BASE_URL}seamguard/detection/video/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading video for detection:', error);
    throw error;
  }
};

export const getVideoDefectDetails = async (token, batchId) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/detection/defect/video?batch_id=${batchId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching video defect details:', error);
    throw error;
  }
};

export const startLiveDetection = async (token, onFrame) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/detection/live`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    // For MJPEG stream
    const reader = response.body.getReader();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += new TextDecoder().decode(value);
      
      // Simple MJPEG frame parsing (simplified for demo)
      const imageStart = buffer.indexOf('\r\n\r\n');
      if (imageStart >= 0) {
        const imageEnd = buffer.indexOf('\r\n--frame', imageStart + 4);
        if (imageEnd >= 0) {
          const imageData = buffer.substring(imageStart + 4, imageEnd);
          buffer = buffer.substring(imageEnd);
          
          // Here you would typically process the frame and defects
          // For demo, we'll just call the callback with a mock defect
          onFrame(URL.createObjectURL(new Blob([imageData], { type: 'image/jpeg' })), [
            { class: 'Broken Stitch', confidence: 0.95 }
          ]);
        }
      }
    }
  } catch (error) {
    console.error('Error starting live detection:', error);
    throw error;
  }
};