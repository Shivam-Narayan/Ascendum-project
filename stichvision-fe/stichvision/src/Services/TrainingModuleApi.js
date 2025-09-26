import API_BASE_URL from '../config';

export const uploadImages = async (files, token) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('images', file);
  });

  try {
    const response = await fetch(`${API_BASE_URL}seamguard/training/upload-image/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to upload images');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading images:', error);
    throw error;
  }
};

export const saveAnnotations = async (imageId, annotations, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/training/save-annotations/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image_id: imageId,
        annotations: annotations.map(ann => ({
          class_name: ann.class,
          x_min: ann.x,
          y_min: ann.y,
          x_max: ann.x + ann.width,
          y_max: ann.y + ann.height
        }))
      })
    });

    if (!response.ok) {
      throw new Error('Failed to save annotations');
    }

    return await response.json();
  } catch (error) {
    console.error('Error saving annotations:', error);
    throw error;
  }
};

export const trainModel = async (epochs, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/training/train-model/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        epochs: epochs
      })
    });

    if (!response.ok) {
      throw new Error('Failed to start model training');
    }

    return await response.json();
  } catch (error) {
    console.error('Error training model:', error);
    throw error;
  }
};