import axios from "axios";
import API_BASE_URL from "../config";

export interface UploadedDocument {
  filename: string;
  file_type: string;
  uploaded_by: string;
  uploaded_at: string;
  source: string;
  num_chunks: number;
  document_id: string;
}

export interface UploadedDocumentsResponse {
  documents: UploadedDocument[];
}

export const getUploadedDocuments = async (): Promise<UploadedDocumentsResponse> => {
  try {
    const response = await axios.get<UploadedDocumentsResponse>(
      `${API_BASE_URL}api/api/uploaded_documents/`
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching uploaded documents:", error);
    throw error;
  }
};