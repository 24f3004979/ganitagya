import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';

// Dynamically sets the API URL based on your build environment.
// In development, it defaults to your local FastAPI server.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request Interceptor 
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    
    // Only log tokens in development to protect user security in production logs
    if (import.meta.env.DEV) {
      console.log(`Adding token payload : ${token}`);
    }

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Standardized Python backend error handling (FastAPI/Flask/Django detail field)
    const backendError = error.response?.data?.detail || error.message || 'Unknown API Error';
    console.error('[API Error]:', backendError);
    return Promise.reject(new Error(backendError));
  }
);

// Reusable, strongly-typed HTTP wrappers
export const api = {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return client.get(url, config);
  },
  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return client.post(url, data, config);
  },
  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return client.put(url, data, config);
  },
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return client.delete(url, config);
  },
};

export default client;

