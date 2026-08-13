import { useState } from 'react';
import { ConversationItem } from '../types/conversation';
import { MOCK_CONVERSATIONS } from '../mock/mockConversationData';

export function useConversationState() {
  const [conversations, setConversations] = useState<ConversationItem[]>(MOCK_CONVERSATIONS);
  const [activeConversationId, setActiveConversationId] = useState<string | null>('conv-01');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentThinkingStage, setCurrentThinkingStage] = useState<string | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const activeConversation = conversations.find((c) => c.id === activeConversationId) || conversations[0];

  const createNewConversation = () => {
    const newConv: ConversationItem = {
      id: `conv_${Date.now()}`,
      title: 'New Conversation',
      createdAt: 'Just now',
      updatedAt: 'Just now',
      messageCount: 0,
      status: 'active',
      messages: [],
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
  };

  const deleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      const remaining = conversations.filter((c) => c.id !== id);
      setActiveConversationId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  const renameConversation = (id: string, newTitle: string) => {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, title: newTitle } : c))
    );
  };

  return {
    conversations,
    setConversations,
    activeConversationId,
    setActiveConversationId,
    activeConversation,
    isStreaming,
    setIsStreaming,
    currentThinkingStage,
    setCurrentThinkingStage,
    isHistoryOpen,
    setIsHistoryOpen,
    searchQuery,
    setSearchQuery,
    createNewConversation,
    deleteConversation,
    renameConversation,
  };
}
