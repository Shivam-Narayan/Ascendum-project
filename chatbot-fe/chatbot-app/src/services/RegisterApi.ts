import axios, { AxiosError } from "axios";
import API_BASE_URL from "../config";

export interface RegisterData {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

type BackendErrorResponse = {
  detail?: string;
  [key: string]: string[] | string | undefined;
};

export const registerUser = async (data: RegisterData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}api/register`, {
      full_name: data.fullName,
      email: data.email,
      password: data.password,
      confirm_password: data.confirmPassword,
    });

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<BackendErrorResponse>;

    if (axiosError.response?.data) {
      // Throw strongly typed backend error
      throw axiosError.response.data;
    }

    throw { detail: "Network error" } as BackendErrorResponse;
  }
};
