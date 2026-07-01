import axios from 'axios';
import { getInitData, tg } from '../lib/telegram';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const initData = getInitData();
    if (initData) {
      config.headers.Authorization = `tghash ${initData}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      
      if (status === 401) {
        tg?.showAlert('Auth error');
      } else if (status === 429) {
        tg?.showAlert('Too many requests');
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
