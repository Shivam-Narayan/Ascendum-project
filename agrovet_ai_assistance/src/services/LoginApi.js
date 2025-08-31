import axios from 'axios';
import API_BASE_URL from '../config'; 

export const loginUser = async (credentials) => {
  try {
    const response = await axios.post(`${API_BASE_URL}user/login/`, credentials);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default loginUser;








