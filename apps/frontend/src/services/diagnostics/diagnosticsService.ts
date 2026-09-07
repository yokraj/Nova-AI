import { apiClient } from '../../lib/axios';

export interface ComponentHealthStatus {
  name: string;
  online: boolean;
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED';
  detail: string;
  latencyMs?: number;
}

export interface RuntimeDiagnosticsSummary {
  overallHealth: 'HEALTHY' | 'DEGRADED' | 'OFFLINE';
  timestamp: string;
  components: ComponentHealthStatus[];
}

export class DiagnosticsService {
  async runFullDiagnostics(): Promise<RuntimeDiagnosticsSummary> {
    const components: ComponentHealthStatus[] = [];

    // 1. Backend REST API
    const startBackend = Date.now();
    try {
      await apiClient.get('/system/health', { timeout: 2000 });
      components.push({
        name: 'FastAPI Backend',
        online: true,
        status: 'ONLINE',
        detail: 'FastAPI server bound on http://localhost:8000/api/v1',
        latencyMs: Date.now() - startBackend,
      });
    } catch {
      components.push({
        name: 'FastAPI Backend',
        online: false,
        status: 'OFFLINE',
        detail: 'Backend server unreachable (offline fallback active)',
      });
    }

    // 2. Database Status
    try {
      await apiClient.get('/system/ready', { timeout: 2000 });
      components.push({
        name: 'Database Storage',
        online: true,
        status: 'ONLINE',
        detail: 'SQLAlchemy database session online & responsive',
      });
    } catch {
      components.push({
        name: 'Database Storage',
        online: false,
        status: 'OFFLINE',
        detail: 'Local SQLite fallback active (.nova_skills_store.json)',
      });
    }

    // 3. Local Ollama LLM Runtime
    const startOllama = Date.now();
    try {
      const res = await fetch('http://127.0.0.1:11434/v1/models', { method: 'GET' });
      const online = res.ok;
      components.push({
        name: 'Ollama Local LLM',
        online,
        status: online ? 'ONLINE' : 'DEGRADED',
        detail: online ? 'Ollama running on port 11434' : 'Ollama endpoint error',
        latencyMs: Date.now() - startOllama,
      });
    } catch {
      components.push({
        name: 'Ollama Local LLM',
        online: false,
        status: 'OFFLINE',
        detail: 'Ollama not running (mock planner fallback active)',
      });
    }

    // 4. Native Bridge Server
    const startBridge = Date.now();
    try {
      const res = await fetch('http://127.0.0.1:3001/health', { method: 'GET' });
      const online = res.ok;
      components.push({
        name: 'Native Bridge Server',
        online,
        status: online ? 'ONLINE' : 'OFFLINE',
        detail: online ? 'Bound to 127.0.0.1:3001' : 'Native Bridge unreachable',
        latencyMs: Date.now() - startBridge,
      });
    } catch {
      components.push({
        name: 'Native Bridge Server',
        online: false,
        status: 'OFFLINE',
        detail: 'Native Bridge offline',
      });
    }

    // 5. Chrome CDP Driver
    try {
      const res = await fetch('http://127.0.0.1:9222/json/version', { method: 'GET' });
      const online = res.ok;
      components.push({
        name: 'Chrome CDP Driver',
        online,
        status: online ? 'ONLINE' : 'OFFLINE',
        detail: online ? 'Connected to Chrome debugging port 9222' : 'Chrome CDP unattached',
      });
    } catch {
      components.push({
        name: 'Chrome CDP Driver',
        online: false,
        status: 'OFFLINE',
        detail: 'Chrome debugging port 9222 not active',
      });
    }

    const onlineCount = components.filter((c) => c.online).length;
    let overallHealth: 'HEALTHY' | 'DEGRADED' | 'OFFLINE' = 'HEALTHY';

    if (onlineCount === 0) {
      overallHealth = 'OFFLINE';
    } else if (onlineCount < components.length) {
      overallHealth = 'DEGRADED';
    }

    return {
      overallHealth,
      timestamp: new Date().toISOString(),
      components,
    };
  }
}

export const diagnosticsService = new DiagnosticsService();
