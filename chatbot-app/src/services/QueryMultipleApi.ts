import axios from "axios";
import API_BASE_URL from "../config";

export interface MultipleQueryResponse {
  answer: string;
  confidence: number;
}

export const askMultipleDocuments = async (
  documentsId: string,
  question: string,
  token: string
): Promise<MultipleQueryResponse> => {
  const response = await axios.post(
    `${API_BASE_URL}api/askm/${documentsId}/`,
    {
      question: question,
    },
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};