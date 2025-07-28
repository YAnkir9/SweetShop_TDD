import React, { useState } from "react";

export default function AdminUsersForm({ user }) {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Fetch all users (admin only)
  const fetchUsers = React.useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/auth/users", {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      } else {
        setError("Failed to fetch users.");
      }
    } catch {
      setError("Network error.");
    }
    setLoading(false);
  }, [user]);

  // Toggle verification for a user
  const toggleVerify = async (userId, is_verified) => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/api/auth/users/${userId}/verify`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${user.token}` },
        body: JSON.stringify({ is_verified: !is_verified })
      });
      if (res.ok) {
        fetchUsers();
      } else {
        setError("Failed to update verification.");
      }
    } catch {
      setError("Network error.");
    }
    setLoading(false);
  };

  // Delete a user
  const handleDelete = async (userId) => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/api/auth/users/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${user.token}` }
      });
      if (res.ok) {
        fetchUsers();
      } else {
        setError("Failed to delete user.");
      }
    } catch {
      setError("Network error.");
    }
    setLoading(false);
  };

  React.useEffect(() => {
    if (user?.role === "admin") fetchUsers();
  }, [user, fetchUsers]);

  return (
    <div style={{ maxWidth: 700, margin: "32px auto", background: "#fff", borderRadius: 12, boxShadow: "0 2px 12px #e0e7ff", padding: 32 }}>
      <h2 style={{ color: "#9333ea", fontWeight: 700, fontSize: "1.5rem", marginBottom: 18 }}>Admin: Manage Users</h2>
      {error && <div style={{ color: "#ef4444", fontWeight: 500, marginBottom: 12 }}>{error}</div>}
      {loading ? (
        <div style={{ color: "#9333ea", fontWeight: 500 }}>Loading users...</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 18 }}>
          <thead>
            <tr style={{ background: "#f3f4f6" }}>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>ID</th>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>Username</th>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>Email</th>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>Verified</th>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>{u.id}</td>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>{u.username}</td>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>{u.email}</td>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>{u.is_verified ? "Yes" : "No"}</td>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>
                  <button style={{ marginRight: 8, background: u.is_verified ? "#f59e42" : "#10b981", color: "#fff", border: "none", borderRadius: 6, padding: "6px 12px", fontWeight: 600, cursor: "pointer" }} onClick={() => toggleVerify(u.id, u.is_verified)}>
                    {u.is_verified ? "Unverify" : "Verify"}
                  </button>
                  <button style={{ background: "#ef4444", color: "#fff", border: "none", borderRadius: 6, padding: "6px 12px", fontWeight: 600, cursor: "pointer" }} onClick={() => handleDelete(u.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
