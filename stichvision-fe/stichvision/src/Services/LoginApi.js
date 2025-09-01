import API_BASE_URL from '../config';

export const loginUser = async (credentials) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Login failed');
    }

    return data;
  } catch (error) {
    throw new Error(error.message || 'Network error occurred');
  }
};