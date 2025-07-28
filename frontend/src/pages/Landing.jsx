import React from "react";
import { Link } from "react-router-dom";

export default function Landing() {
  // Use a local image or a solid color for background. Example uses a public image.
  const backgroundStyle = {
    backgroundColor: '#f3f4f6', // Tailwind gray-100
    minHeight: '100vh',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
  };

  return (
    <div style={backgroundStyle}>
      {/* Navbar moved to App.jsx */}
      <div className="flex flex-1 items-center justify-center mt-12">
        <div className="bg-white p-10 rounded-xl shadow-2xl w-full max-w-md text-center border-2 border-pink-200">
          <h1 className="text-4xl font-extrabold mb-6 text-pink-600">Welcome to SweetShop!</h1>
          <p className="text-gray-700 text-lg mb-4">Discover the best sweets, browse our inventory, and enjoy a delightful shopping experience.</p>
          <div className="flex justify-center space-x-4 mt-6">
            <Link to="/login" className="px-6 py-2 rounded bg-blue-500 text-white hover:bg-blue-600 transition font-semibold">Login</Link>
            <Link to="/register" className="px-6 py-2 rounded bg-purple-500 text-white hover:bg-purple-600 transition font-semibold">Register</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
