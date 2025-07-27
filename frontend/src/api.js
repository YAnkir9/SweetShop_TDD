import axios from 'axios';

const getApiBaseUrl = () => {
  if (import.meta.env.MODE === 'development') {
    return import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  }
  // Production or other environments
  return import.meta.env.VITE_API_URL || '/api';
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  withCredentials: true, // if you need cookies/auth
});

export default api;
