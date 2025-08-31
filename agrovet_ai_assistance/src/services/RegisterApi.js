import axios from 'axios';
import API_BASE_URL from "../config";

export const registerUser = async (name, email, password, confirmPassword) => {
  try {
    const response = await axios.post(`${API_BASE_URL}user/register/`, {
      name: name,
      email: email,
      password: password,
      confirm_password: confirmPassword,
    });

    return response.data; 
  } catch (error) {
    throw new Error(error.response?.data?.detail || "Registration failed");
  }
};

export default registerUser;