import React, { useState, useEffect } from "react";

export default function AdminStockReport({ user }) {
  const [stock, setStock] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user?.role === "admin") {
      setLoading(true);
      setError("");
      fetch("/api/stock-report", {
        headers: { Authorization: `Bearer ${user.token}` }
      })
        .then(res => res.ok ? res.json() : Promise.reject("Failed to fetch stock report"))
        .then(data => setStock(data))
        .catch(err => setError(typeof err === "string" ? err : "Network error."))
        .finally(() => setLoading(false));
    }
  }, [user]);

  return (
    <div style={{ maxWidth: 900, margin: "32px auto", background: "#fff", borderRadius: 12, boxShadow: "0 2px 12px #e0e7ff", padding: 32 }}>
      <h2 style={{ color: "#9333ea", fontWeight: 700, fontSize: "1.5rem", marginBottom: 18 }}>Admin: Stock Report</h2>
      {error && <div style={{ color: "#ef4444", fontWeight: 500, marginBottom: 12 }}>{error}</div>}
      {loading ? (
        <div style={{ color: "#9333ea", fontWeight: 500 }}>Loading stock report...</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 18 }}>
          <thead>
            <tr style={{ background: "#f3f4f6" }}>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>Sweet</th>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>Category</th>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>Current Stock</th>
              <th style={{ padding: "10px 8px", border: "1px solid #e5e7eb" }}>Price</th>
            </tr>
          </thead>
          <tbody>
            {stock.map(item => (
              <tr key={item.sweet_id}>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>{item.sweet_name}</td>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>{item.category_name}</td>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>{item.quantity}</td>
                <td style={{ padding: "8px", border: "1px solid #e5e7eb" }}>₹{item.price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
