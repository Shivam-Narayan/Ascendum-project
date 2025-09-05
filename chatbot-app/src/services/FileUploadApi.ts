import axios from 'axios';
import API_BASE_URL from '../config';

export interface UploadResponse {
  status: string;
  pdf_id: string;
  metadata: {
    processing_time: number;
    total_chunks: number;
    total_tables: number;
    total_images: number;
    content_length: number;
  };
  tables: number;
  images: number;
  chunks: number;
}

export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Get authorization token
  const token = localStorage.getItem('token');
  
  try {
    const response = await axios.post(`${API_BASE_URL}api/upload-pdf/`, formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('File upload error:', error);
    
    if (axios.isAxiosError(error)) {
      throw new Error(`Upload failed: ${error.response?.data?.message || error.response?.statusText || error.message}`);
    }
    
    throw new Error('Upload failed: Unknown error');
  }
};