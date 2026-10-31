export const APP_CONFIG = {
  name: 'Nova AI Operating System',
  version: '1.0.0',
  backendBaseUrl: 'http://localhost:8000',
  apiBaseUrl: 'http://localhost:8000/api/v1',
  nativeBridgeUrl: 'http://127.0.0.1:3001',
  ollamaBaseUrl: 'http://127.0.0.1:11434',
  wsUrl: 'ws://localhost:8000/ws/dashboard',
  useMockData: false,
  defaultWorkspace: 'Nova',
  defaultTheme: 'dark' as const,
  requestTimeoutMs: 8000,
  maxRetries: 2,
};
