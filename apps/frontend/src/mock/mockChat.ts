import { ChatMessage } from '@/types';

export const MOCK_CHAT_MESSAGES: ChatMessage[] = [
  {
    id: 'msg-1',
    role: 'user',
    content: 'Explain Nova AI Operating System Architecture and Memory Platform layers.',
    timestamp: '14:00:10',
  },
  {
    id: 'msg-2',
    role: 'assistant',
    content:
      'Nova AI Operating System features a modular local-first architecture powered by 7 core Memory Platform subsystems: Universal Intelligence Engine, Memory Foundation, Vector Memory, Hybrid RAG, Knowledge Graph, Code Intelligence, and Context Engine, routed via the Inference Gateway.',
    timestamp: '14:00:12',
    model: 'llama3.2',
    provider: 'ollama',
    tokens: 48,
  },
];
