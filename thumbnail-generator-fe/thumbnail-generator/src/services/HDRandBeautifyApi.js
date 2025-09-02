// import API_BASE_URL from '../config';

// export const enhanceThumbnail = async (thumbnailUrl, hdr, beautify) => {
//   try {
//     const formData = new FormData();

//     // Extract the relative path from the full URL
//     const relativeThumbnailUrl = thumbnailUrl.replace(API_BASE_URL, '/'); // Remove the base URL

//     formData.append('thumbnail_url', relativeThumbnailUrl);
//     formData.append('hdr', hdr);
//     formData.append('beautify', beautify);

//     // Retrieve the token (assuming it's stored in localStorage)
//     const token = localStorage.getItem('token'); // Replace 'authToken' with your token key

//     const response = await fetch(`${API_BASE_URL}accounts/enhance_thumbnailhdr/`, {
//       method: 'POST',
//       headers: {
//         Authorization: `Bearer ${token}`, // Add the Authorization header
//       },
//       body: formData,
//     });

//     if (!response.ok) {
//       throw new Error(`HTTP error! status: ${response.status}`);
//     }

//     const blob = await response.blob(); // Assuming the API returns an image
//     return URL.createObjectURL(blob); // Create a URL for the enhanced image
//   } catch (error) {
//     console.error('Error enhancing thumbnail:', error);
//     throw error;
//   }
// };

import API_BASE_URL from '../config';

/**
 * Enhance a thumbnail with HDR and/or Beautify effects.
 * @param {string} thumbnailUrl - The URL of the thumbnail to enhance.
 * @param {boolean} hdr - Whether to apply HDR effect.
 * @param {boolean} beautify - Whether to apply Beautify effect.
 * @returns {Promise<string>} - A promise that resolves to the enhanced image URL (base64).
 */
export const enhanceThumbnail = async (thumbnailUrl, hdr, beautify) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Authentication token not found');
    }

    let relativeThumbnailUrl;
    try {
      if (thumbnailUrl.startsWith('http')) {
        const url = new URL(thumbnailUrl);
        relativeThumbnailUrl = url.pathname;
      } else {
        relativeThumbnailUrl = thumbnailUrl;
      }
    } catch (e) {
      console.error('Error parsing thumbnail URL:', e);
      relativeThumbnailUrl = thumbnailUrl;
    }

    const formData = new FormData();
    formData.append('thumbnail_url', relativeThumbnailUrl);
    formData.append('hdr', hdr);
    formData.append('beautify', beautify);

    const response = await fetch(`${API_BASE_URL}accounts/enhance_thumbnailhdr/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'Failed to enhance thumbnail');
    }

    const blob = await response.blob();
    console.log('Blob response:', blob); // Debug log
    return URL.createObjectURL(blob);
  } catch (error) {
    console.error('Error enhancing thumbnail:', error);
    throw error;
  }
};