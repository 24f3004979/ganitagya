import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://ganitagya.onrender.com';

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

    if (import.meta.env.DEV) {
      console.log(`Token present: ${Boolean(token)}`);
    }

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: only normalizes errors, no longer unwraps data
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const backendError = error.response?.data?.detail || error.message || 'Unknown API Error';
    console.error('[API Error]:', backendError);
    return Promise.reject(new Error(backendError));
  }
);

// Typed wrappers: unwrap .data here
export const api = {
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await client.get<T>(url, config);
    return res.data;
  },
  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await client.post<T>(url, data, config);
    return res.data;
  },
  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await client.put<T>(url, data, config);
    return res.data;
  },
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await client.delete<T>(url, config);
    return res.data;
  },
};

export default client;
