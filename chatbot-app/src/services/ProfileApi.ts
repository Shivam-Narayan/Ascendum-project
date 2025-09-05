import axios from "axios";
import API_BASE_URL from "../config";

export interface Profile {
  id: number;
  full_name: string;
  email: string;
  registered_at: string;
}

export const getProfile = async (): Promise<Profile> => {
  try {
    const response = await axios.get(`${API_BASE_URL}api/profile/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching profile:", error);
    throw error;
  }
};
