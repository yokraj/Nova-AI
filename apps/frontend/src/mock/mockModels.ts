import { ModelInfo } from '@/types';

export const MOCK_MODELS: ModelInfo[] = [
  {
    name: 'llama3.2',
    provider: 'ollama',
    contextWindow: 131072,
    supportsVision: false,
    status: 'online',
  },
  {
    name: 'llama3.1:70b',
    provider: 'vllm',
    contextWindow: 131072,
    supportsVision: false,
    status: 'online',
  },
  {
    name: 'gpt-4o',
    provider: 'openai',
    contextWindow: 128000,
    supportsVision: true,
    status: 'online',
  },
];
