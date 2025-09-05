import axios from "axios";
import API_BASE_URL from "../config";

interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export const changePassword = async (payload: ChangePasswordPayload) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}api/changePassword/`,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
        },
      }
    );
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      // Error came from Axios
      throw new Error(error.response?.data?.error || "Failed to change password");
    }
    // Non-Axios error (unexpected)
    throw new Error("Network error, please try again");
  }
};
