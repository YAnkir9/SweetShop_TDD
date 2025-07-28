import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Register({ onRegister }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [address_line1, setAddressLine1] = useState("");
  const [address_line2, setAddressLine2] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [postal_code, setPostalCode] = useState("");
  const [country, setCountry] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          email,
          password,
          address_line1,
          address_line2,
          city,
          state,
          postal_code,
          country
        }),
      });
      if (res.ok) {
        setSuccess("Registration successful! Redirecting to login...");
        setTimeout(() => {
          navigate("/login");
        }, 2000);
        if (onRegister) {
          const data = await res.json();
          onRegister(data);
        }
      } else {
        const err = await res.json();
        setError(err.detail || "Registration failed");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6', padding: '32px 0', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100vw', boxSizing: 'border-box' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px', width: '100%' }}>
        <h2 style={{ fontSize: '2.2rem', fontWeight: 700, color: '#22223b', marginBottom: '8px', letterSpacing: '0.5px' }}>Register for SweetShop</h2>
        <p style={{ color: '#374151', fontSize: '1.1rem' }}>Create your account to continue</p>
      </div>
      <div style={{ width: '100%', maxWidth: '520px', margin: '0 auto' }}>
        <form style={{ background: '#fff', borderRadius: '12px', boxShadow: '0 2px 12px rgba(0,0,0,0.07)', padding: '32px 24px', border: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '18px' }} onSubmit={handleSubmit}>
          {error && <div style={{ color: '#ef4444', fontWeight: 500, background: '#fee2e2', borderRadius: '8px', padding: '8px 0', width: '100%', textAlign: 'center', fontSize: '1.1rem', marginBottom: '8px' }}>{error}</div>}
          {success && <div style={{ color: '#22c55e', fontWeight: 500, background: '#dcfce7', borderRadius: '8px', padding: '8px 0', width: '100%', textAlign: 'center', fontSize: '1.1rem', marginBottom: '8px' }}>{success}</div>}
          <input type="text" placeholder="Username" style={{ width: '100%', padding: '12px', border: '2px solid #a78bfa', borderRadius: '8px', fontSize: '1.1rem', background: '#f3e8ff', marginBottom: '8px' }} value={username} onChange={e => setUsername(e.target.value)} required disabled={loading} />
          <input type="email" placeholder="Email" style={{ width: '100%', padding: '12px', border: '2px solid #f472b6', borderRadius: '8px', fontSize: '1.1rem', background: '#fdf2f8', marginBottom: '8px' }} value={email} onChange={e => setEmail(e.target.value)} required disabled={loading} />
          <input type="password" placeholder="Password" style={{ width: '100%', padding: '12px', border: '2px solid #60a5fa', borderRadius: '8px', fontSize: '1.1rem', background: '#eff6ff', marginBottom: '8px' }} value={password} onChange={e => setPassword(e.target.value)} required disabled={loading} />
          <input type="text" placeholder="Address Line 1" style={{ width: '100%', padding: '12px', border: '2px solid #d1d5db', borderRadius: '8px', fontSize: '1.1rem', background: '#f9fafb', marginBottom: '8px' }} value={address_line1} onChange={e => setAddressLine1(e.target.value)} disabled={loading} />
          <input type="text" placeholder="Address Line 2" style={{ width: '100%', padding: '12px', border: '2px solid #d1d5db', borderRadius: '8px', fontSize: '1.1rem', background: '#f9fafb', marginBottom: '8px' }} value={address_line2} onChange={e => setAddressLine2(e.target.value)} disabled={loading} />
          <input type="text" placeholder="City" style={{ width: '100%', padding: '12px', border: '2px solid #d1d5db', borderRadius: '8px', fontSize: '1.1rem', background: '#f9fafb', marginBottom: '8px' }} value={city} onChange={e => setCity(e.target.value)} disabled={loading} />
          <input type="text" placeholder="State" style={{ width: '100%', padding: '12px', border: '2px solid #d1d5db', borderRadius: '8px', fontSize: '1.1rem', background: '#f9fafb', marginBottom: '8px' }} value={state} onChange={e => setState(e.target.value)} disabled={loading} />
          <input type="text" placeholder="Postal Code" style={{ width: '100%', padding: '12px', border: '2px solid #d1d5db', borderRadius: '8px', fontSize: '1.1rem', background: '#f9fafb', marginBottom: '8px' }} value={postal_code} onChange={e => setPostalCode(e.target.value)} disabled={loading} />
          <input type="text" placeholder="Country" style={{ width: '100%', padding: '12px', border: '2px solid #d1d5db', borderRadius: '8px', fontSize: '1.1rem', background: '#f9fafb', marginBottom: '8px' }} value={country} onChange={e => setCountry(e.target.value)} disabled={loading} />
          <button style={{ width: '100%', background: '#9333ea', color: '#fff', border: 'none', borderRadius: '8px', padding: '12px', fontWeight: 600, fontSize: '1.1rem', cursor: 'pointer', marginTop: '8px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', transition: 'background 0.2s' }} disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        <div style={{ marginTop: '18px', textAlign: 'center' }}>
          <Link to="/dashboard" style={{ color: '#9333ea', fontWeight: 600, fontSize: '1.1rem', textDecoration: 'underline' }}>Go to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
