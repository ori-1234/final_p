import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Set default credentials for all axios requests
axios.defaults.withCredentials = true;

// Create axios instance with default config
const api = axios.create({
    baseURL: (import.meta?.env?.VITE_API_URL || 'http://localhost:8000') + '/api/',
    withCredentials: true,  // Important for cookies
    headers: {
        'Content-Type': 'application/json',
    }
});

// Add a request interceptor
api.interceptors.request.use(
    (config) => {
        // You can add auth headers here if needed
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add a response interceptor
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Do NOT hard-refresh the page on 401. Propagate the error and let
        // route guards/UI handle navigation and messaging gracefully.
        // This prevents full-page reloads on bad credentials.
        // If you need centralized handling for protected areas,
        // implement it in the AuthContext or route guards.
        // if (error.response?.status === 401) {
        //   // Optionally emit an event or set a global flag here
        // }
        return Promise.reject(error);
    }
);

export default api;