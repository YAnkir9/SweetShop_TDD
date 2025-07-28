import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// Landing page removed
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import { Link } from "react-router-dom";

export default function App() {
  const [user, setUser] = useState(() => {
    // Restore session from localStorage if present
    const saved = localStorage.getItem("sweetshop_user_session");
    return saved ? JSON.parse(saved) : null;
  });

  // Save session to localStorage on login
  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem("sweetshop_user_session", JSON.stringify(userData));
  };

  // Clear session on logout
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("sweetshop_user_session");
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard user={user} onLogout={handleLogout} />} />
        <Route path="/dashboard" element={<Dashboard user={user} onLogout={handleLogout} />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/register" element={<Register onRegister={handleLogin} />} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}
