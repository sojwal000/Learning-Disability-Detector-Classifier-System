import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    console.log('[API DEBUG] Making request to:', config.url);
    console.log('[API DEBUG] Token exists:', !!token);
    if (token) {
      console.log('[API DEBUG] Token preview:', token.substring(0, 20) + '...');
      config.headers.Authorization = `Bearer ${token}`;
      console.log('[API DEBUG] Authorization header set');
    } else {
      console.log('[API DEBUG] No token found in localStorage');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log('[API DEBUG] Response error:', error.response?.status, error.response?.data);
    if (error.response?.status === 401) {
      console.log('[API DEBUG] 401 Unauthorized - clearing auth and redirecting to login');
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
