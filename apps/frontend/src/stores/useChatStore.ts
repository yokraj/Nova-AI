import { create } from 'zustand';
import { ChatMessage } from '@/types';
import { MOCK_CHAT_MESSAGES } from '@/mock/mockChat';

interface ChatState {
  messages: ChatMessage[];
  selectedModel: string;
  selectedProvider: string;
  addMessage: (message: ChatMessage) => void;
  setModel: (model: string) => void;
  setProvider: (provider: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: MOCK_CHAT_MESSAGES,
  selectedModel: 'llama3.2',
  selectedProvider: 'ollama',
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setModel: (selectedModel) => set({ selectedModel }),
  setProvider: (selectedProvider) => set({ selectedProvider }),
}));
