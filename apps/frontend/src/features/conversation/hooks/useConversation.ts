import { useRef } from 'react';
import { useConversationState } from './useConversationState';
import { ConversationMessage, AttachmentFile } from '../types/message';
import { executeRealStreamingResponse } from '../services/realConversationEngine';

export function useConversation() {
  const convState = useConversationState();
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSendMessage = (prompt: string, attachments?: AttachmentFile[]) => {
    if (!prompt.trim() || !convState.activeConversationId) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const userMsg: ConversationMessage = {
      id: `msg_user_${Date.now()}`,
      role: 'user',
      content: prompt,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status: 'complete',
      attachments,
    };

    const assistantMsgId = `msg_nova_${Date.now()}`;
    const initialAssistantMsg: ConversationMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status: 'thinking',
      thinkingStage: 'UNDERSTANDING',
    };

    // Update conversation with user message and initial thinking assistant message
    convState.setConversations((prev) =>
      prev.map((c) => {
        if (c.id === convState.activeConversationId) {
          const updatedMessages = [...c.messages, userMsg, initialAssistantMsg];
          const newTitle = c.messages.length === 0 ? prompt.substring(0, 35) + '...' : c.title;
          return {
            ...c,
            title: newTitle,
            messageCount: updatedMessages.length,
            messages: updatedMessages,
          };
        }
        return c;
      })
    );

    convState.setIsStreaming(true);
    convState.setCurrentThinkingStage('UNDERSTANDING');

    // Extract prior turns for multi-turn conversational context
    const currentConv = convState.conversations.find((c) => c.id === convState.activeConversationId);
    const priorTurns = (currentConv?.messages || [])
      .filter((m) => m.content && m.status === 'complete')
      .map((m) => ({ role: m.role, content: m.content }));

    // Run real streaming response from backend / Ollama
    executeRealStreamingResponse(
      prompt,
      (update) => {
        convState.setCurrentThinkingStage(update.thinkingStage || null);

        convState.setConversations((prev) =>
          prev.map((c) => {
            if (c.id === convState.activeConversationId) {
              return {
                ...c,
                messages: c.messages.map((m) => {
                  if (m.id === assistantMsgId) {
                    return {
                      ...m,
                      status: update.isComplete ? 'complete' : 'streaming',
                      thinkingStage: update.thinkingStage,
                      blocks: update.blocks || m.blocks,
                      content:
                        update.blocks && update.blocks[0]?.content
                          ? update.blocks[0].content
                          : update.streamingContent || m.content,
                    };
                  }
                  return m;
                }),
              };
            }
            return c;
          })
        );

        if (update.isComplete) {
          convState.setIsStreaming(false);
          convState.setCurrentThinkingStage(null);
        }
      },
      abortController.signal,
      priorTurns,
      convState.activeConversationId
    );
  };

  const handleStopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    convState.setIsStreaming(false);
    convState.setCurrentThinkingStage(null);
  };

  const handleRegenerate = (msgId: string) => {
    if (!convState.activeConversation) return;
    const msg = convState.activeConversation.messages.find((m) => m.id === msgId);
    if (msg) {
      handleSendMessage(msg.content);
    }
  };

  const handleApproveAction = (msgId: string, approvalId: string) => {
    convState.setConversations((prev) =>
      prev.map((c) => {
        if (c.id === convState.activeConversationId) {
          return {
            ...c,
            messages: c.messages.map((m) => {
              if (m.id === msgId && m.blocks) {
                return {
                  ...m,
                  blocks: m.blocks.map((b) => {
                    if (b.type === 'approval' && b.approvalData && b.approvalData.id === approvalId) {
                      return {
                        ...b,
                        approvalData: {
                          ...b.approvalData,
                          status: 'approved',
                        },
                      };
                    }
                    return b;
                  }),
                };
              }
              return m;
            }),
          };
        }
        return c;
      })
    );
  };

  const handleRejectAction = (msgId: string, approvalId: string) => {
    convState.setConversations((prev) =>
      prev.map((c) => {
        if (c.id === convState.activeConversationId) {
          return {
            ...c,
            messages: c.messages.map((m) => {
              if (m.id === msgId && m.blocks) {
                return {
                  ...m,
                  blocks: m.blocks.map((b) => {
                    if (b.type === 'approval' && b.approvalData && b.approvalData.id === approvalId) {
                      return {
                        ...b,
                        approvalData: {
                          ...b.approvalData,
                          status: 'rejected',
                        },
                      };
                    }
                    return b;
                  }),
                };
              }
              return m;
            }),
          };
        }
        return c;
      })
    );
  };

  return {
    ...convState,
    handleSendMessage,
    handleStopStreaming,
    handleRegenerate,
    handleApproveAction,
    handleRejectAction,
  };
}
