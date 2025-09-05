import axios, { AxiosError } from "axios";
import API_BASE_URL from "../config";
import type { UserHistoryItem } from "../types/chat";

export interface LoginData {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: {
    id: number;
    full_name: string;
    email: string;
  };
  user_history: UserHistoryItem[];
}

type BackendErrorResponse = {
  detail?: string;
  [key: string]: string[] | string | undefined;
};

export const loginUser = async (data: LoginData): Promise<LoginResponse> => {
  try {
    const response = await axios.post<LoginResponse>(
      `${API_BASE_URL}api/login`,
      data
    );
    localStorage.setItem("userHistory", JSON.stringify(response.data.user_history));
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<BackendErrorResponse>;
    if (axiosError.response?.data) {
      throw axiosError.response.data;
    }
    throw { detail: "Network error" } as BackendErrorResponse;
  }
};