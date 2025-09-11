import axios, { AxiosError } from "axios";
import API_BASE_URL from "../config";

export interface UploadResponse {
  status: string;
  documents: Array<{
    document_id: string;
    filename: string;
    num_chunks: number;
  }>;
}

export interface UploadError {
  error: string;
  details?: string;
}

export const uploadDatabaseFile = async (files: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append("files", files);

  try {
    const response = await axios.post<UploadResponse>(
      `${API_BASE_URL}api/api/upload_document/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
        },
        timeout: 30000, // 30 seconds timeout
      }
    );

    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ error?: string; details?: string }>;
      if (axiosError.response) {
        throw {
          error: axiosError.response.data?.error || "Upload failed",
          details: axiosError.response.data?.details || "Please try again later",
        } as UploadError;
      } else if (axiosError.request) {
        throw {
          error: "Network error",
          details: "Please check your internet connection and try again",
        } as UploadError;
      }
    }

    // Fallback for non-Axios errors
    throw {
      error: "Upload failed",
      details: error instanceof Error ? error.message : "An unexpected error occurred",
    } as UploadError;
  }
};
