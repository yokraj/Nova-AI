import { ConversationMessage } from './message';

export interface ConversationItem {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  tags?: string[];
  status: 'active' | 'archived';
  messages: ConversationMessage[];
}

export interface ConversationState {
  conversations: ConversationItem[];
  activeConversationId: string | null;
  isStreaming: boolean;
  currentThinkingStage: string | null;
  isHistoryOpen: boolean;
  searchQuery: string;
}
