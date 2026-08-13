import React from 'react';
import { ConversationMessage } from '../types/message';
import UserMessage from './UserMessage';
import NovaMessage from './NovaMessage';
import ConversationEmptyState from './ConversationEmptyState';

interface ConversationThreadProps {
  messages: ConversationMessage[];
  onSelectPrompt: (prompt: string) => void;
  onRegenerateMessage?: (msgId: string) => void;
  onApproveAction?: (msgId: string, approvalId: string) => void;
  onRejectAction?: (msgId: string, approvalId: string) => void;
  className?: string;
}

export const ConversationThread: React.FC<ConversationThreadProps> = ({
  messages,
  onSelectPrompt,
  onRegenerateMessage,
  onApproveAction,
  onRejectAction,
  className,
}) => {
  if (messages.length === 0) {
    return <ConversationEmptyState onSelectPrompt={onSelectPrompt} className={className} />;
  }

  return (
    <div className="space-y-4 pb-24">
      {messages.map((msg) => {
        if (msg.role === 'user') {
          return <UserMessage key={msg.id} message={msg} />;
        }
        return (
          <NovaMessage
            key={msg.id}
            message={msg}
            onRegenerate={() => onRegenerateMessage?.(msg.id)}
            onApproveAction={(appId) => onApproveAction?.(msg.id, appId)}
            onRejectAction={(appId) => onRejectAction?.(msg.id, appId)}
          />
        );
      })}
    </div>
  );
};

export default ConversationThread;
