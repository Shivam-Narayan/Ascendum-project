import React, { useState, useEffect } from "react";
import "./UserManagement.css";
import { fetchUsers, deleteUser } from "../../../Services/UserManagementApi";

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState({
    isOpen: false,
    user: null,
  });
  const [notification, setNotification] = useState({
    isOpen: false,
    message: "",
    type: "",
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Fetch users from API
  useEffect(() => {
    const getUsers = async () => {
      try {
        setLoading(true);
        const usersData = await fetchUsers();
        setUsers(usersData);
        setError(null);
      } catch (err) {
        setError(err.message || "Failed to fetch users");
        console.error("Error fetching users:", err);
      } finally {
        setLoading(false);
      }
    };

    getUsers();
  }, []);

  const handleDeleteClick = (user) => {
    setDeleteConfirm({
      isOpen: true,
      user: user,
    });
  };

  const confirmDelete = async () => {
    if (deleteConfirm.user) {
      try {
        await deleteUser(deleteConfirm.user.emp_id);
        setUsers(users.filter((u) => u.emp_id !== deleteConfirm.user.emp_id));
        setError(null);
        setNotification({
          isOpen: true,
          message: `User ${deleteConfirm.user.name} (${deleteConfirm.user.emp_id}) deleted successfully.`,
          type: "success",
        });
      } catch (err) {
        setError(err.message || "Failed to delete user");
        console.error("Error deleting user:", err);
        setNotification({
          isOpen: true,
          message: "Failed to delete user.",
          type: "error",
        });
      }
    }
    setDeleteConfirm({ isOpen: false, user: null });
  };

  useEffect(() => {
    if (notification.isOpen) {
      const timer = setTimeout(() => {
        setNotification({ ...notification, isOpen: false });
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const cancelDelete = () => {
    setDeleteConfirm({ isOpen: false, user: null });
  };

  // Filter users based on search query
  const filteredUsers = users.filter((user) =>
    Object.values(user)
      .join(" ")
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="usermanagement-container">
        <div className="usermanagement-loading">Loading users...</div>
      </div>
    );
  }

  if (error && !deleteConfirm.isOpen) {
    return (
      <div className="usermanagement-container">
        <div className="usermanagement-error-message">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="usermanagement-container">
      {/* Search Bar */}
      <div className={`usermanagement-search-bar ${isSearchOpen ? "usermanagement-open" : ""}`}>
        <input
          type="text"
          placeholder="Search by anything..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button
          className="usermanagement-search-icon"
          onClick={() => setIsSearchOpen(!isSearchOpen)}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            height="20"
            viewBox="0 0 24 24"
            width="20"
            fill="#555"
          >
            <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 
            6.5 6.5 0 109.5 16c1.61 0 3.09-.59 
            4.23-1.57l.27.28v.79l5 4.99L20.49 
            19l-4.99-5zm-6 0C8.01 14 6 11.99 
            6 9.5S8.01 5 10.5 5 15 7.01 
            15 9.5 12.99 14 10.5 14z" />
          </svg>
        </button>
      </div>

      <div className="usermanagement-table-wrapper">
        <div className="usermanagement-table-container">
          <table className="usermanagement-table">
            <thead>
              <tr>
                <th>Emp ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone Number</th>
                <th>Line Number</th>
                <th>Department</th>
                <th>Created At</th>
                <th>Updated At</th>
                <th>Active</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user, idx) => (
                  <tr key={idx}>
                    <td>{user.emp_id}</td>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>{user.phone_number}</td>
                    <td>{user.line_number}</td>
                    <td>{user.department}</td>
                    <td>{new Date(user.created_at).toLocaleString()}</td>
                    <td>{new Date(user.updated_at).toLocaleString()}</td>
                    <td>
                      <span
                        className={`usermanagement-status ${
                          user.is_active ? "usermanagement-active" : "usermanagement-inactive"
                        }`}
                      >
                        {user.is_active ? "Yes" : "No"}
                      </span>
                    </td>
                    <td>
                      <button
                        className="usermanagement-delete-btn"
                        onClick={() => handleDeleteClick(user)}
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="10">
                    <div className="usermanagement-no-data-container">
                      <div className="usermanagement-no-data">No users found</div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {deleteConfirm.isOpen && (
        <div className="usermanagement-dialog-overlay">
          <div className="usermanagement-confirmation-dialog">
            <h3>Confirm Delete</h3>
            <p>
              Are you sure you want to delete user{" "}
              <strong>{deleteConfirm.user?.name}</strong> (
              {deleteConfirm.user?.emp_id})? This action cannot be undone.
            </p>
            <div className="usermanagement-dialog-actions">
              <button className="usermanagement-cancel-btn" onClick={cancelDelete}>
                Cancel
              </button>
              <button className="usermanagement-confirm-delete-btn" onClick={confirmDelete}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {notification.isOpen && (
        <div className={`usermanagement-notification ${notification.type}`}>
          {notification.message}
        </div>
      )}
    </div>
  );
}

export default UserManagement;