import axios from "axios";
import API_BASE_URL from "../config";

export interface ExcelUploadResponse {
  status: string;
  dataset_id: string;
  rows: number;
  columns: number;
  columns_list: string[];
}

export async function uploadExcelOrCsv(
  file: File,
  token: string
): Promise<ExcelUploadResponse> {
  try {
    if (!token) {
      throw new Error("No authentication token found. Please login again.");
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post<ExcelUploadResponse>(
      `${API_BASE_URL}api/upload-csv/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error: unknown) {
    console.error("Excel/CSV upload failed:", error);
    if (axios.isAxiosError(error) && error.response) {
      throw error.response.data;
    }
    throw error;
  }
}

