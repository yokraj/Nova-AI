export interface ModelConfig {
  provider: 'LOCAL' | 'OPTIONAL_CLOUD' | 'MOCK';
  baseUrl: string;
  model: string;
  temperature: number;
  maxTokens: number;
  timeoutMs: number;
  enableLocalModel: boolean;
  fallbackToMock: boolean;
}

const DEFAULT_CONFIG: ModelConfig = {
  provider: 'LOCAL',
  baseUrl: 'http://127.0.0.1:11434/v1',
  model: 'llama3.2',
  temperature: 0.1,
  maxTokens: 2048,
  timeoutMs: 30000,
  enableLocalModel: true,
  fallbackToMock: true,
};

const STORAGE_KEY = 'nova_model_config';

export class ModelConfigStore {
  private static config: ModelConfig = ModelConfigStore.loadConfig();

  private static loadConfig(): ModelConfig {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const stored = window.localStorage.getItem(STORAGE_KEY);
        if (stored) {
          return { ...DEFAULT_CONFIG, ...JSON.parse(stored) };
        }
      }
    } catch {
      // Fall back to default config if storage unreadable
    }
    return { ...DEFAULT_CONFIG };
  }

  static getConfig(): ModelConfig {
    return { ...this.config };
  }

  static updateConfig(newConfig: Partial<ModelConfig>): ModelConfig {
    this.config = { ...this.config, ...newConfig };
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(this.config));
      }
    } catch {
      // Ignore storage errors
    }
    return { ...this.config };
  }

  static resetConfig(): ModelConfig {
    this.config = { ...DEFAULT_CONFIG };
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // Ignore storage errors
    }
    return { ...this.config };
  }
}
