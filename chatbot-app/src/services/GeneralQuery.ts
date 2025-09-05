import axios, { AxiosError } from "axios";
import API_BASE_URL from "../config";

interface GeneralResponse {
  question: string;
  answer: string;
}

export async function askGeneral(
  question: string,
  token: string
): Promise<GeneralResponse> {
  try {
    const response = await axios.post<GeneralResponse>(
      `${API_BASE_URL}api/chat/`,
      { question },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  } catch (err) {
    const error = err as AxiosError<{ detail?: string }>;
    if (error.response) {
      throw new Error(error.response.data?.detail || "Server error");
    }
    throw new Error(error.message || "Network error");
  }
}
