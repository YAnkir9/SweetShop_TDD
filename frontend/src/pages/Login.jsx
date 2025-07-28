import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        const tokenData = await res.json();
        // Fetch user details by email for session info
        const encodedEmail = encodeURIComponent(email);
        const userRes = await fetch(`/api/auth/users/by-email/${encodedEmail}`, {
          headers: { Authorization: `Bearer ${tokenData.access_token}` }
        });
        if (userRes.ok) {
          const userData = await userRes.json();
          if (userData.is_verified === false) {
            setError("Your account is not verified. Please contact admin.");
            setLoading(false);
            return;
          }
          if (onLogin) onLogin({ ...userData, token: tokenData.access_token });
          window.alert("Login successful! Welcome, " + (userData.username || userData.email));
          navigate("/dashboard");
        } else {
          setError("Failed to fetch user info after login.");
        }
      } else {
        const err = await res.json();
        setError(err.detail || "Login failed");
      }
    } catch {
      setError("Network error. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6', padding: '32px 0', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100vw', boxSizing: 'border-box' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px', width: '100%' }}>
        <h2 style={{ fontSize: '2.2rem', fontWeight: 700, color: '#22223b', marginBottom: '8px', letterSpacing: '0.5px' }}>Login to SweetShop</h2>
        <p style={{ color: '#374151', fontSize: '1.1rem' }}>Enter your credentials to continue</p>
      </div>
      <div style={{ width: '100%', maxWidth: '420px', margin: '0 auto' }}>
        <form style={{ background: '#fff', borderRadius: '12px', boxShadow: '0 2px 12px rgba(0,0,0,0.07)', padding: '32px 24px', border: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '18px' }} onSubmit={handleSubmit}>
          {error && <div style={{ color: '#ef4444', fontWeight: 500, background: '#fee2e2', borderRadius: '8px', padding: '8px 0', width: '100%', textAlign: 'center', fontSize: '1.1rem', marginBottom: '8px' }}>{error}</div>}
          <input type="email" placeholder="Email" style={{ width: '100%', padding: '12px', border: '2px solid #93c5fd', borderRadius: '8px', fontSize: '1.1rem', background: '#eff6ff', marginBottom: '8px' }} value={email} onChange={e => setEmail(e.target.value)} required disabled={loading} />
          <input type="password" placeholder="Password" style={{ width: '100%', padding: '12px', border: '2px solid #c4b5fd', borderRadius: '8px', fontSize: '1.1rem', background: '#f3e8ff', marginBottom: '8px' }} value={password} onChange={e => setPassword(e.target.value)} required disabled={loading} />
          <button style={{ width: '100%', background: '#9333ea', color: '#fff', border: 'none', borderRadius: '8px', padding: '12px', fontWeight: 600, fontSize: '1.1rem', cursor: 'pointer', marginTop: '8px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', transition: 'background 0.2s' }} disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        <div style={{ marginTop: '18px', textAlign: 'center' }}>
          <Link to="/dashboard" style={{ color: '#9333ea', fontWeight: 600, fontSize: '1.1rem', textDecoration: 'underline' }}>Go to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
