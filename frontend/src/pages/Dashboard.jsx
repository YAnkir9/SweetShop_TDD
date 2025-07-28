import React, { useEffect, useState } from "react";
// onLogout prop added for logout button
// Dynamically import all images from assets
const sweetImages = import.meta.glob('../assets/*.jpg', { eager: true });
import { fetchSweets } from "./api";


export default function Dashboard({ user, onLogout, setUser }) {
  const [grouped, setGrouped] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchSweets(1, 20)
      .then((data) => {
        // Group sweets by category
        const items = Array.isArray(data) ? data : data.items || [];
        const byCat = {};
        items.forEach(sweet => {
          const catName = sweet.category?.name || "Other";
          if (!byCat[catName]) byCat[catName] = [];
          byCat[catName].push(sweet);
        });
        setGrouped(Object.entries(byCat));
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to load sweets.");
        setLoading(false);
        console.error("API error:", err);
      });

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
  }, [user]);

  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6', padding: '32px 0', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100vw', boxSizing: 'border-box', position: 'relative' }}>
      {/* User info at top right */}
      {user && (
        <div style={{ position: 'absolute', top: 24, right: 48, background: '#fff', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.07)', padding: '10px 22px', fontWeight: 600, color: '#9333ea', fontSize: '1.1rem', zIndex: 10, display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span>Welcome, {user.username || user.email}!</span>
          <button
            style={{ padding: '6px 18px', borderRadius: '6px', background: '#ef4444', color: '#fff', fontWeight: '600', fontSize: '1rem', border: 'none', boxShadow: '0 1px 4px #fecaca', cursor: 'pointer', transition: 'background 0.2s' }}
            onClick={() => onLogout && onLogout()}
          >Logout</button>
        </div>
      )}
      <div style={{ textAlign: 'center', marginBottom: '32px', width: '100%' }}>
        <h2 style={{ fontSize: '2.2rem', fontWeight: 700, color: '#22223b', marginBottom: '8px', letterSpacing: '0.5px' }}>Sweet Categories</h2>
        <p style={{ color: '#374151', fontSize: '1.1rem' }}>Browse sweets by category</p>
      </div>
      <div style={{ width: '100%', maxWidth: '1200px', margin: '0 auto' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: '#9333ea', fontWeight: 500 }}>Loading sweets...</div>
        ) : error ? (
          <div style={{ textAlign: 'center', color: '#ef4444', fontWeight: 500 }}>{error}</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '40px', alignItems: 'center', width: '100%' }}>
            {grouped.map(([catName, sweets]) => (
              <div key={catName} style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 600, color: '#9333ea', marginBottom: '18px', letterSpacing: '0.5px', textAlign: 'center' }}>{catName}</h3>
                <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', justifyContent: 'center', width: '100%' }}>
                  {sweets.map((sweet) => {
                    // Improved image logic with logging
                    // Always use local asset image matched by sweet name
                    const assetName = sweet.name.toLowerCase().replace(/ /g, '_');
                    let imgSrc = `/assets/${assetName}.jpg`;
                    // Helper to check if image exists (async)
                    // For best UX, show alt text if image fails to load
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
                            style={{ width: '120px', height: '120px', objectFit: 'cover', borderRadius: '8px' }}
                            onError={e => {
                              e.target.onerror = null;
                              e.target.style.display = 'none';
                              e.target.parentNode.innerHTML += `<span style='color:#9333ea;font-weight:600;font-size:1rem;'>No Image</span>`;
                            }}
                          />
                        </div>
                        <span style={{ fontWeight: 500, fontSize: '1.05rem', color: '#22223b', marginTop: '2px' }}>{sweet.name}</span>
                        <span style={{ color: '#6b7280', fontSize: '0.95rem', marginTop: '6px', minHeight: '20px' }}>{sweet.description || ''}</span>
                        <span style={{ color: '#9333ea', fontWeight: 600, marginTop: '8px', fontSize: '1.1rem' }}>₹{sweet.price}</span>
                        <button
                          style={{ marginTop: '14px', background: '#9333ea', color: '#fff', border: 'none', borderRadius: '6px', padding: '8px 18px', fontWeight: 600, cursor: 'pointer', fontSize: '1rem', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', transition: 'background 0.2s' }}
                          onMouseOver={e => e.target.style.background = '#7c2ae8'}
                          onMouseOut={e => e.target.style.background = '#9333ea'}
                          onClick={async () => {
                            if (!user) {
                              alert('Please log in to buy sweets!');
                              return;
                            }
                            try {
                              const res = await fetch('/api/purchases', {
                                method: 'POST',
                                headers: {
                                  'Content-Type': 'application/json',
                                  ...(user?.token ? { 'Authorization': `Bearer ${user.token}` } : {})
                                },
                                body: JSON.stringify({ sweet_id: sweet.id, quantity: 1 })
                              });
                              if (res.ok) {
                                alert(`Purchase successful for ${sweet.name}!`);
                              } else {
                                const err = await res.json();
                                alert(`Purchase failed: ${err.detail || 'Unknown error'}`);
                              }
                            } catch (err) {
                              alert('Network error. Please try again.');
                            }
                          }}
                        >Buy</button>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
