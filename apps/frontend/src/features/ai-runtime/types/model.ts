export type ModelProviderType = 'LOCAL' | 'OPTIONAL_CLOUD' | 'MOCK';

export interface ModelCapabilities {
  supportsToolCalling: boolean;
  supportsVision: boolean;
  supportsStreaming: boolean;
  contextWindowTokens: number;
}

export interface ModelInfo {
  id: string;
  name: string;
  providerType: ModelProviderType;
  endpointUrl?: string;
  capabilities: ModelCapabilities;
  isAvailable: boolean;
}
