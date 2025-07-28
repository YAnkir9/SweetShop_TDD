import React, { useEffect, useState } from "react";
import AdminSweetsForm from "./AdminSweetsForm";
import AdminStockReport from "./AdminStockReport";
import AdminUsersForm from "./AdminUsersForm";
// onLogout prop added for logout button
// Dynamically import all images from assets
const sweetImages = import.meta.glob('../assets/*.jpg', { eager: true });
import { fetchSweets } from "./api";


export default function Dashboard({ user, onLogout, setUser }) {
  const [search, setSearch] = useState("");
  const [grouped, setGrouped] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshFlag, setRefreshFlag] = useState(0); // triggers data reload

  useEffect(() => {
    setLoading(true);
    setError("");
    // If user is logged in, send JWT; else fetch public sweets
    const fetchSweetsData = async () => {
      try {
        let res;
        if (user?.token) {
          res = await fetch('/api/sweets', {
            headers: { 'Authorization': `Bearer ${user.token}` }
          });
        } else {
          res = await fetch('/api/sweets');
        }
        if (!res.ok) throw new Error('Failed to load sweets');
        const data = await res.json();
        const items = Array.isArray(data) ? data : data.items || [];
        const byCat = {};
        items.forEach(sweet => {
          const catName = sweet.category?.name || "Other";
          if (!byCat[catName]) byCat[catName] = [];
          byCat[catName].push(sweet);
        });
        setGrouped(Object.entries(byCat));
      } catch (err) {
        setError("Failed to load sweets.");
        console.error("API error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSweetsData();

    // Only fetch user info if user.token exists (i.e., after login)
    if (user && user.email && user.token && typeof setUser === 'function') {
      const encodedEmail = encodeURIComponent(user.email);
      fetch(`/api/auth/users/by-email/${encodedEmail}`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      })
        .then(res => {
          if (!res.ok) throw new Error('User info fetch failed');
          return res.json();
        })
        .then(data => {
          if (data.is_verified === false) {
            setError('Your account is not verified. Please contact admin.');
            setUser(null); // Log out user
            return;
          }
          setUser({ ...user, ...data });
        })
        .catch(err => {
          setError('Failed to fetch user info after login.');
          console.error('Failed to fetch user info:', err);
        });
    }
  }, [user, setUser, refreshFlag]);

  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6', padding: '32px 0', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100vw', boxSizing: 'border-box', position: 'relative' }}>
      {/* Navbar with single logout button */}
      <nav style={{ width: '100%', background: '#fff', boxShadow: '0 2px 8px #e0e7ff', padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 100 }}>
        <span style={{ fontWeight: 'bold', fontSize: '1.5rem', color: '#9333ea' }}>Sweet Shop Dashboard</span>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
            <span style={{ color: '#9333ea', fontWeight: '600', fontSize: '1.1rem' }}>Welcome, {user.username || user.email}!</span>
            <button
              style={{ padding: '8px 22px', borderRadius: '8px', background: '#ef4444', color: '#fff', fontWeight: '600', fontSize: '1.05rem', border: 'none', boxShadow: '0 2px 8px #fecaca', cursor: 'pointer', transition: 'background 0.2s' }}
              onClick={() => onLogout && onLogout()}
            >Logout</button>
          </div>
        ) : (
          <div style={{ marginBottom: '18px', fontWeight: 500, color: '#ef4444', background: '#f3f4f6', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
            You are not logged in. <br />
            <a href="/login" style={{ color: '#9333ea', fontWeight: 600, marginRight: '12px', textDecoration: 'underline' }}>Login</a>
            or
            <a href="/register" style={{ color: '#9333ea', fontWeight: 600, marginLeft: '12px', textDecoration: 'underline' }}>Register</a>
            to buy sweets and access your dashboard features.
          </div>
        )}
      </nav>
      {/* Admin forms for add/update/delete sweets and manage users */}
      {user?.role === "admin"
        ? (
          <>
            <div style={{ width: '100%', maxWidth: '1200px', margin: '32px auto', display: 'flex', gap: '32px', flexWrap: 'wrap', justifyContent: 'center' }}>
              <div style={{ flex: 1, minWidth: 350, background: 'linear-gradient(135deg, #f3f4f6 0%, #e0e7ff 100%)', borderRadius: 16, boxShadow: '0 4px 24px #e0e7ff', padding: 24 }}>
                <AdminSweetsForm user={user} onSweetAdded={() => setRefreshFlag(f => f + 1)} onSweetUpdated={() => setRefreshFlag(f => f + 1)} onSweetDeleted={() => setRefreshFlag(f => f + 1)} />
              </div>
              <div style={{ flex: 1, minWidth: 350, background: 'linear-gradient(135deg, #f3f4f6 0%, #e0e7ff 100%)', borderRadius: 16, boxShadow: '0 4px 24px #e0e7ff', padding: 24 }}>
                <AdminUsersForm user={user} onUserChanged={() => setRefreshFlag(f => f + 1)} />
              </div>
            </div>
            <div style={{ margin: '32px auto', width: '100%', maxWidth: '900px', background: 'linear-gradient(135deg, #f3f4f6 0%, #e0e7ff 100%)', borderRadius: 16, boxShadow: '0 4px 24px #e0e7ff', padding: 24 }}>
              <AdminStockReport user={user} refreshFlag={refreshFlag} />
            </div>
          </>
        )
        : (
          <>
            <div style={{ textAlign: 'center', marginBottom: '32px', width: '100%' }}>
              <h2 style={{ fontSize: '2.2rem', fontWeight: 700, color: '#22223b', marginBottom: '8px', letterSpacing: '0.5px' }}>Sweet Categories</h2>
              <p style={{ color: '#374151', fontSize: '1.1rem' }}>Browse sweets by category</p>
            </div>
            <div style={{ width: '100%', maxWidth: '1200px', margin: '0 auto' }}>
              <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <input
                  type="text"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search sweets by name or category..."
                  style={{ padding: '10px 18px', borderRadius: '8px', border: '1px solid #c7d2fe', fontSize: '1.1rem', width: '320px', marginTop: '8px' }}
                />
              </div>
              {loading ? (
                <div style={{ textAlign: 'center', color: '#9333ea', fontWeight: 500 }}>Loading sweets...</div>
              ) : error ? (
                <div style={{ textAlign: 'center', color: '#ef4444', fontWeight: 500 }}>{error}</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '40px', alignItems: 'center', width: '100%' }}>
                  {grouped.map(([catName, sweets]) => {
                    // Filter sweets by search
                    const filteredSweets = sweets.filter(sweet =>
                      sweet.name.toLowerCase().includes(search.toLowerCase()) ||
                      catName.toLowerCase().includes(search.toLowerCase())
                    );
                    if (filteredSweets.length === 0) return null;
                    return (
                      <div key={catName} style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <h3 style={{ fontSize: '1.3rem', fontWeight: 600, color: '#9333ea', marginBottom: '18px', letterSpacing: '0.5px', textAlign: 'center' }}>{catName}</h3>
                        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', justifyContent: 'center', width: '100%' }}>
                          {filteredSweets.map((sweet) => {
                            const assetName = sweet.name.toLowerCase().replace(/ /g, '_');
                            let imgSrc = `/assets/${assetName}.jpg`;
                            if (imgSrc === sweetImages['../assets/no_image.jpg']) {
                              console.log(`Sweet: ${sweet.name} | No image found, using placeholder.`);
                            } else {
                              console.log(`Sweet: ${sweet.name} | Using local asset: ${assetName}.jpg`);
                            }
                            return (
                              <div key={sweet.id} style={{ background: '#fff', borderRadius: '12px', boxShadow: '0 2px 12px rgba(0,0,0,0.07)', width: 'calc(25% - 24px)', minWidth: '200px', maxWidth: '260px', textAlign: 'center', padding: '18px 12px', border: '1px solid #e5e7eb', transition: 'box-shadow 0.2s', display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '24px' }}>
                                <div style={{ width: '120px', height: '120px', marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f3f4f6', borderRadius: '8px', boxShadow: '0 1px 6px rgba(0,0,0,0.08)' }}>
                                  <img
                                    src={imgSrc}
                                    alt={sweet.name}
                                    style={{ width: '120px', height: '120px', objectFit: 'cover', borderRadius: '8px', filter: sweet.quantity === 0 ? 'grayscale(0.7) brightness(1.2)' : 'none', opacity: sweet.quantity === 0 ? 0.7 : 1 }}
                                    onError={e => {
                                      e.target.onerror = null;
                                      e.target.style.display = 'none';
                                      e.target.parentNode.innerHTML += `<span style='color:#9333ea;font-weight:600;font-size:1rem;'>No Image</span>`;
                                    }}
                                  />
                                  {sweet.quantity === 0 && (
                                    user?.role === 'customer' ? (
                                      <span style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', background: 'rgba(255,255,255,0.8)', color: '#ef4444', fontWeight: 700, fontSize: '1.1rem', padding: '6px 18px', borderRadius: '8px', boxShadow: '0 2px 8px #fecaca', pointerEvents: 'none', zIndex: 2, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '4px' }}>
                                          <circle cx="10" cy="10" r="10" fill="#ef4444"/>
                                          <text x="10" y="15" textAnchor="middle" fontSize="12" fill="#fff" fontWeight="bold">!</text>
                                        </svg>
                                        Sold Out (Customer Only)
                                      </span>
                                    ) : (
                                      <span style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', background: 'rgba(255,255,255,0.8)', color: '#ef4444', fontWeight: 700, fontSize: '1.1rem', padding: '6px 18px', borderRadius: '8px', boxShadow: '0 2px 8px #fecaca', pointerEvents: 'none', zIndex: 2 }}>Sold Out</span>
                                    )
                                  )}
                                </div>
                                <span style={{ fontWeight: 500, fontSize: '1.05rem', color: '#22223b', marginTop: '2px' }}>{sweet.name}</span>
                                <span style={{ color: '#6b7280', fontSize: '0.95rem', marginTop: '6px', minHeight: '20px' }}>{sweet.description || ''}</span>
                                <span style={{ color: '#9333ea', fontWeight: 600, marginTop: '8px', fontSize: '1.1rem' }}>₹{sweet.price}</span>
                                <button
                                  style={{ marginTop: '14px', background: sweet.quantity === 0 ? '#d1d5db' : '#9333ea', color: '#fff', border: 'none', borderRadius: '6px', padding: '8px 18px', fontWeight: 600, cursor: sweet.quantity === 0 ? 'not-allowed' : 'pointer', fontSize: '1rem', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', transition: 'background 0.2s' }}
                                  disabled={sweet.quantity === 0}
                                  onMouseOver={e => { if (sweet.quantity !== 0) e.target.style.background = '#7c2ae8'; }}
                                  onMouseOut={e => { if (sweet.quantity !== 0) e.target.style.background = '#9333ea'; }}
                                  onClick={async () => {
                                    if (!user) {
                                      alert('Please log in to buy sweets!');
                                      return;
                                    }
                                    if (sweet.quantity === 0) return;
                                    try {
                                      const res = await fetch('/api/purchases', {
                                        method: 'POST',
                                        headers: {
                                          'Content-Type': 'application/json',
                                          ...(user?.token ? { 'Authorization': `Bearer ${user.token}` } : {})
                                        },
                                        body: JSON.stringify({ sweet_id: sweet.id, quantity: 1 })
                                      });
                                      if (res.status === 401) {
                                        alert('Session expired. Please log in again.');
                                        if (typeof onLogout === 'function') onLogout();
                                        return;
                                      }
                                      if (res.ok) {
                                        alert(`Purchase successful for ${sweet.name}!`);
                                      } else {
                                        const err = await res.json();
                                        alert(`Purchase failed: ${err.detail || 'Unknown error'}`);
                                      }
                                    } catch {
                                      alert('Network error. Please try again.');
                                    }
                                  }}
                                >{sweet.quantity === 0 ? 'Out of Stock' : 'Buy'}</button>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}
    </div>
  );
}
