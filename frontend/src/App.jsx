import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// Landing page removed
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import { Link } from "react-router-dom";

export default function App() {
  const [user, setUser] = useState(null);

  return (
    <Router>
      <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #f3f4f6 0%, #e0e7ff 100%)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', paddingTop: '80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <span style={{ fontWeight: 'bold', fontSize: '2.8rem', color: '#7c3aed', letterSpacing: '1px', textShadow: '0 2px 8px #e0e7ff' }}>Sweet Shop</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '32px', marginBottom: '48px', alignItems: 'center' }}>
          {!user && <Link to="/login" style={{ padding: '12px 32px', borderRadius: '8px', background: '#e0e7ff', color: '#7c3aed', textDecoration: 'none', fontWeight: '600', fontSize: '1.1rem', boxShadow: '0 2px 8px #c7d2fe', border: '1px solid #c7d2fe', transition: 'background 0.2s' }}>Login</Link>}
          {!user && <Link to="/register" style={{ padding: '12px 32px', borderRadius: '8px', background: '#f3f4f6', color: '#9333ea', textDecoration: 'none', fontWeight: '600', fontSize: '1.1rem', boxShadow: '0 2px 8px #e0e7ff', border: '1px solid #e0e7ff', transition: 'background 0.2s' }}>Register</Link>}
          {user && (
            <>
              <span style={{ color: '#9333ea', fontWeight: '600', fontSize: '1.1rem', marginRight: '18px' }}>Welcome, {user.username || user.email}!</span>
              <button
                style={{ padding: '10px 24px', borderRadius: '8px', background: '#ef4444', color: '#fff', fontWeight: '600', fontSize: '1.05rem', border: 'none', boxShadow: '0 2px 8px #fecaca', cursor: 'pointer', transition: 'background 0.2s' }}
                onClick={() => setUser(null)}
              >Logout</button>
            </>
          )}
        </div>
        <div style={{ width: '100%' }}>
          <Routes>
            <Route path="/" element={<Dashboard user={user} onLogout={() => setUser(null)} />} />
            <Route path="/dashboard" element={<Dashboard user={user} onLogout={() => setUser(null)} />} />
            <Route path="/login" element={<Login onLogin={setUser} />} />
            <Route path="/register" element={<Register onRegister={setUser} />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}
