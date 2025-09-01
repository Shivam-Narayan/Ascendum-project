import axios from "axios";
import API_BASE_URL from "../config";

export interface ExcelQueryResponse {
  question: string;
  answer: string;
  confidence: number;
  method: string;
  analysis_data: Record<string, unknown>;
  plan_executed: Record<string, unknown>;
}

export async function askDataset(
  datasetId: string,
  question: string
): Promise<ExcelQueryResponse> {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("No authentication token found. Please login again.");
    }

    const response = await axios.post<ExcelQueryResponse>(
      `${API_BASE_URL}api/ask-data/${datasetId}/`,
      { question },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("Dataset query failed:", error.response?.data || error.message);
      throw error.response?.data || error.message;
    }
    console.error("Unexpected error:", error);
    throw error;
  }
}
