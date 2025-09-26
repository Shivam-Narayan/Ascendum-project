import API_BASE_URL from "../config";

// Fetch all users
export const fetchUsers = async () => {
  try {
    const token = localStorage.getItem("adminToken");
    if (!token) {
      throw new Error("No authentication token found");
    }

    const response = await fetch(`${API_BASE_URL}seamguard/admin/users/list/`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication failed. Please login again.");
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching users:", error);
    throw error;
  }
};

// Delete a user
export const deleteUser = async (empId) => {
  try {
    const token = localStorage.getItem("adminToken");
    if (!token) {
      throw new Error("No authentication token found");
    }

    const response = await fetch(`${API_BASE_URL}seamguard/admin/users/${empId}/delete/`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication failed. Please login again.");
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return true;
  } catch (error) {
    console.error("Error deleting user:", error);
    throw error;
  }
};

// Fetch Admin Analytics
export const fetchAdminAnalytics = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/admin/users/all/`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch analytics");
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
};

// Fetch user reports by employee ID
export const fetchUserReports = async (employeeId, token) => {
  if (!employeeId) {
    throw new Error("⚠️ Please enter an Employee ID");
  }

  const response = await fetch(
    `${API_BASE_URL}seamguard/admins/users/${employeeId}/`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error("Invalid Employee ID or No Data Found");
  }

  const data = await response.json();

  if (!data.length) {
    throw new Error("No reports available for this Employee ID");
  }

  return data[0];
};