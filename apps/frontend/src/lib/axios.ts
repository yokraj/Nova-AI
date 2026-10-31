import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { APP_CONFIG } from '../config/app.config';

function createConfiguredClient(baseURL: string): AxiosInstance {
  const instance = axios.create({
    baseURL,
    timeout: APP_CONFIG.requestTimeoutMs || 8000,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  });

  // Attach Authorization Bearer token from localStorage or dev environment
  instance.interceptors.request.use((config) => {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      const meta = import.meta as any;
      const devToken = meta?.env?.DEV ? (meta.env.VITE_DEV_AUTH_TOKEN as string | undefined) : undefined;
      const token = localStorage.getItem('nova_auth_token') || devToken;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  });

  // Response interceptor for consistent error normalization
  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const config = error.config as AxiosRequestConfig & { _retryCount?: number };
      if (!config) return Promise.reject(error);

      config._retryCount = config._retryCount || 0;
      const isNetworkError = !error.response;
      const is5xx = error.response && error.response.status >= 500 && error.response.status < 600;

      // Retry transient network or 5xx errors up to maxRetries
      if ((isNetworkError || is5xx) && config._retryCount < APP_CONFIG.maxRetries) {
        config._retryCount += 1;
        const delay = Math.min(1000 * Math.pow(2, config._retryCount), 3000);
        await new Promise((resolve) => setTimeout(resolve, delay));
        return instance(config);
      }

      return Promise.reject(error);
    }
  );

  return instance;
}

export const apiClient = createConfiguredClient(APP_CONFIG.apiBaseUrl);
export const backendClient = createConfiguredClient(APP_CONFIG.backendBaseUrl);
