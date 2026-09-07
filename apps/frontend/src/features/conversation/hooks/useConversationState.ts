import { useState, useEffect } from 'react';
import { ConversationItem } from '../types/conversation';
import { MOCK_CONVERSATIONS } from '../mock/mockConversationData';
import { conversationApiService } from '../../../services/api/conversationApiService';
import { PersistenceState } from '../../../components/PersistenceStatusIndicator';

export function useConversationState() {
  const [conversations, setConversations] = useState<ConversationItem[]>(MOCK_CONVERSATIONS);
  const [activeConversationId, setActiveConversationId] = useState<string | null>('conv-01');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentThinkingStage, setCurrentThinkingStage] = useState<string | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [persistenceState, setPersistenceState] = useState<PersistenceState>('OFFLINE');

  useEffect(() => {
    let isMounted = true;
    async function loadBackendConversations() {
      setPersistenceState('SYNCING');
      try {
        const remoteConvs = await conversationApiService.listConversations();
        if (isMounted && remoteConvs && remoteConvs.length > 0) {
          const mapped: ConversationItem[] = remoteConvs.map((rc) => ({
            id: rc.id,
            title: rc.title,
            createdAt: rc.createdAt ? new Date(rc.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Just now',
            updatedAt: rc.updatedAt ? new Date(rc.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Just now',
            messageCount: 0,
            status: rc.status as any || 'active',
            messages: [],
          }));
          setConversations(mapped);
          setActiveConversationId(mapped[0].id);
          setPersistenceState('PERSISTED');
        } else if (isMounted) {
          setPersistenceState('OFFLINE');
        }
      } catch (err) {
        if (isMounted) setPersistenceState('OFFLINE');
      }
    }
    loadBackendConversations();
    return () => {
      isMounted = false;
    };
  }, []);

  const activeConversation = conversations.find((c) => c.id === activeConversationId) || conversations[0];

  const createNewConversation = async () => {
    setPersistenceState('SYNCING');
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

    try {
      const created = await conversationApiService.createConversation('New Conversation');
      if (created && created.id) {
        setConversations((prev) =>
          prev.map((c) => (c.id === newConv.id ? { ...c, id: created.id } : c))
        );
        setActiveConversationId(created.id);
        setPersistenceState('PERSISTED');
      } else {
        setPersistenceState('OFFLINE');
      }
    } catch (err) {
      setPersistenceState('OFFLINE');
    }
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
    persistenceState,
  };
}
