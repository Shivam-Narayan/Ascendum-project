import axios from "axios";
import API_BASE_URL from "../config";

export interface MultipleFileUploadResponse {
  documents_id: string;
  details: Array<{
    filename: string;
    status: "success" | "error";
    file_type: "PDF" | "WORD" | "EXCEL" | "CSV" | "OTHER";
    error_message?: string;
  }>;
}

export const uploadMultipleFiles = async (
  files: File[],
  token: string
): Promise<MultipleFileUploadResponse> => {
  const formData = new FormData();
  
  // Add each file to the form data
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await axios.post(
    `${API_BASE_URL}api/multiple/`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};