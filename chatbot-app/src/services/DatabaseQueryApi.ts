import axios from 'axios';
import API_BASE_URL from '../config';

export interface QueryResult {
  chunk_id: string;
  document_id: string;
  page: number;
  content: string;
  score: number;
  metadata: {
    filename: string;
    file_type: string;
    uploaded_by: string;
  };
}

export interface QueryResponse {
  query: string;
  answer: string;
  results: QueryResult[];
}

export interface QueryError {
  error: string;
  details?: string;
}

export const queryDocument = async (
  query: string,
  filename?: string
): Promise<QueryResponse> => {
  try {
    const payload = filename ? { query, filename } : { query };
    
    const response = await axios.post<QueryResponse>(
      `${API_BASE_URL}api/api/query_document/`,
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const errorData = error.response?.data;
      throw {
        error: errorData?.error || 'Query failed',
        details: errorData?.details || error.message,
      } as QueryError;
    }
    
    throw {
      error: 'Query failed',
      details: error instanceof Error ? error.message : 'Unknown error occurred',
    } as QueryError;
  }
};