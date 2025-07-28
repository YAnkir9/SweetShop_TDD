import React, { useState } from "react";

export default function AdminSweetsForm({ user, onSweetAdded, onSweetUpdated, onSweetDeleted }) {
  const [form, setForm] = useState({
    name: "",
    price: "",
    category_id: "",
    image_url: "",
    description: ""
  });
  const [sweetId, setSweetId] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async e => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const res = await fetch("/api/sweets", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.token}`
        },
        body: JSON.stringify(form)
      });
      if (res.ok) {
        setMessage("Sweet added successfully!");
        setForm({ name: "", price: "", category_id: "", image_url: "", description: "" });
        if (onSweetAdded) onSweetAdded();
      } else {
        const err = await res.json();
        setMessage(err.detail || "Failed to add sweet.");
      }
    } catch {
      setMessage("Network error.");
    }
    setLoading(false);
  };

  const handleUpdate = async e => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const res = await fetch(`/api/sweets/${sweetId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.token}`
        },
        body: JSON.stringify(form)
      });
      if (res.ok) {
        setMessage("Sweet updated successfully!");
        if (onSweetUpdated) onSweetUpdated();
      } else {
        const err = await res.json();
        setMessage(err.detail || "Failed to update sweet.");
      }
    } catch {
      setMessage("Network error.");
    }
    setLoading(false);
  };

  const handleDelete = async e => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const res = await fetch(`/api/sweets/${sweetId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${user.token}`
        }
      });
      if (res.ok) {
        setMessage("Sweet deleted successfully!");
        if (onSweetDeleted) onSweetDeleted();
      } else {
        const err = await res.json();
        setMessage(err.detail || "Failed to delete sweet.");
      }
    } catch {
      setMessage("Network error.");
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: "32px auto", background: "#fff", borderRadius: 12, boxShadow: "0 2px 12px #e0e7ff", padding: 32 }}>
      <h2 style={{ color: "#9333ea", fontWeight: 700, fontSize: "1.5rem", marginBottom: 18 }}>Admin: Manage Sweets</h2>
      {message && <div style={{ color: message.includes("success") ? "#10b981" : "#ef4444", fontWeight: 500, marginBottom: 12 }}>{message}</div>}
      <form onSubmit={handleAdd} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <input name="name" value={form.name} onChange={handleChange} placeholder="Sweet Name" required style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="price" value={form.price} onChange={handleChange} placeholder="Price" required type="number" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="category_id" value={form.category_id} onChange={handleChange} placeholder="Category ID" required type="number" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="image_url" value={form.image_url} onChange={handleChange} placeholder="Image URL" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="description" value={form.description} onChange={handleChange} placeholder="Description" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <button type="submit" disabled={loading} style={{ background: "#9333ea", color: "#fff", padding: "10px 0", borderRadius: 8, fontWeight: 600, border: "none", marginTop: 8 }}>Add Sweet</button>
      </form>
      <hr style={{ margin: "24px 0" }} />
      <form onSubmit={handleUpdate} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <input value={sweetId} onChange={e => setSweetId(e.target.value)} placeholder="Sweet ID (for update/delete)" required type="number" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="name" value={form.name} onChange={handleChange} placeholder="New Name" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="price" value={form.price} onChange={handleChange} placeholder="New Price" type="number" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="category_id" value={form.category_id} onChange={handleChange} placeholder="New Category ID" type="number" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="image_url" value={form.image_url} onChange={handleChange} placeholder="New Image URL" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <input name="description" value={form.description} onChange={handleChange} placeholder="New Description" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <button type="submit" disabled={loading} style={{ background: "#f59e42", color: "#fff", padding: "10px 0", borderRadius: 8, fontWeight: 600, border: "none", marginTop: 8 }}>Update Sweet</button>
      </form>
      <form onSubmit={handleDelete} style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 18 }}>
        <input value={sweetId} onChange={e => setSweetId(e.target.value)} placeholder="Sweet ID (for delete)" required type="number" style={{ padding: 10, borderRadius: 8, border: "1px solid #c7d2fe" }} />
        <button type="submit" disabled={loading} style={{ background: "#ef4444", color: "#fff", padding: "10px 0", borderRadius: 8, fontWeight: 600, border: "none", marginTop: 8 }}>Delete Sweet</button>
      </form>
    </div>
  );
}
