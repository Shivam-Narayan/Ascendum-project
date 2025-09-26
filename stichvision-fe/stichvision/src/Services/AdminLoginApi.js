import API_BASE_URL from "../config";

export const adminLogin = async (credentials) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/admin/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      // Handle backend error
      const errorData = await response.json();
      throw new Error(errorData.detail || "Admin login failed");
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
};