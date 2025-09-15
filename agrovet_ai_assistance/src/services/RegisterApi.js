import axios from 'axios';
import API_BASE_URL from "../config";

export const registerUser = async (userData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}user/register/`, {
      name: userData.name,
      email: userData.email,
      password: userData.password,
      confirm_password: userData.confirmPassword,
    }, 
    {
      headers: { 'Content-Type': 'application/json' },
    });

    return response.data; 
  } catch (error) {
    // Handle validation errors from backend
    if (error.response?.data) {
      // If backend returns field-specific errors
      if (typeof error.response.data === 'object' && !error.response.data.detail) {
        throw error.response.data; // Return the validation errors object
      }
      // If backend returns a general error message
      throw new Error(error.response.data.detail || error.response.data.message || "Registration failed");
    }
    // Network or other errors
    throw new Error("Registration failed. Please check your connection and try again.");
  }
};

export default registerUser;