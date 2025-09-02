import API_BASE_URL from '../config';

/**
 * Logs out the user by sending a POST request to the backend logout endpoint.
 * 
 * @param {string} token - The user's authentication token.
 * @returns {Promise<object>} - A promise that resolves to the response data.
 */
const logoutUser = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}accounts/logout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to log out');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Logout API error:', error.message);
    throw error;
  }
};

export default logoutUser;