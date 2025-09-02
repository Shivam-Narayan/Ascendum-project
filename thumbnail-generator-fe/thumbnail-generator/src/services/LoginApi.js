import API_BASE_URL from '../config';

export const loginuser = async (email, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}accounts/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle different error cases
      if (data.detail) {
        throw new Error(data.detail);
      }
      if (data.message) {
        throw new Error(data.message);
      }
      throw new Error("Login failed");
    }

    // Make sure we have the token
    if (!data.token) {
      throw new Error("No authentication token received");
    }

    return {
      token: data.token,
      message: data.message || "Login successful"
    };
  } catch (error) {
    console.error("Login API error:", error);
    throw new Error(error.message || "Network error. Please try again.");
  }
};

export default loginuser;