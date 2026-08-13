import React from 'react';
import { useConversation } from '../hooks/useConversation';
import ConversationHeader from './ConversationHeader';
import ConversationThread from './ConversationThread';
import ConversationComposer from './ConversationComposer';
import ConversationHistoryDrawer from './ConversationHistoryDrawer';

export const ConversationWorkspace: React.FC = () => {
  const {
    conversations,
    activeConversationId,
    activeConversation,
    isStreaming,
    isHistoryOpen,
    setIsHistoryOpen,
    createNewConversation,
    deleteConversation,
    renameConversation,
    setActiveConversationId,
    handleSendMessage,
    handleStopStreaming,
    handleRegenerate,
    handleApproveAction,
    handleRejectAction,
  } = useConversation();

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)] max-w-5xl mx-auto relative bg-slate-950/60 rounded-3xl border border-slate-900 overflow-hidden shadow-2xl">
      {/* 1. Header Bar */}
      <ConversationHeader
        title={activeConversation ? activeConversation.title : 'New Conversation'}
        onNewChat={createNewConversation}
        onToggleHistory={() => setIsHistoryOpen(true)}
      />

      {/* 2. Scrollable Thread Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 scrollbar-thin scrollbar-thumb-slate-800">
        <ConversationThread
          messages={activeConversation ? activeConversation.messages : []}
          onSelectPrompt={(p) => handleSendMessage(p)}
          onRegenerateMessage={(msgId) => handleRegenerate(msgId)}
          onApproveAction={(msgId, appId) => handleApproveAction(msgId, appId)}
          onRejectAction={(msgId, appId) => handleRejectAction(msgId, appId)}
        />
      </div>

      {/* 3. Sticky Bottom Composer */}
      <div className="p-4 bg-gradient-to-t from-slate-950 via-slate-950/90 to-transparent">
        <ConversationComposer
          onSendMessage={(p, atts) => handleSendMessage(p, atts)}
          isStreaming={isStreaming}
          onStopStreaming={handleStopStreaming}
        />
      </div>

      {/* 4. Slide-Over History Drawer */}
      <ConversationHistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        conversations={conversations}
        activeId={activeConversationId}
        onSelectConversation={(id) => setActiveConversationId(id)}
        onNewChat={createNewConversation}
        onDeleteConversation={deleteConversation}
        onRenameConversation={renameConversation}
      />
    </div>
  );
};

export default ConversationWorkspace;
