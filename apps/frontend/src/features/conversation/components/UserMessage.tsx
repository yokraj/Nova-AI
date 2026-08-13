import React from 'react';
import { User, Paperclip, Clock } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ConversationMessage } from '../types/message';

export const UserMessage: React.FC<{ message: ConversationMessage; className?: string }> = ({ message, className }) => {
  return (
    <div className={cn('flex items-start space-x-3 justify-end my-4', className)}>
      <div className="max-w-2xl space-y-2 text-right">
        {/* User Content Bubble */}
        <div className="inline-block p-4 rounded-3xl rounded-tr-sm bg-gradient-to-r from-cyan-600/30 to-blue-600/30 border border-cyan-500/40 text-slate-100 shadow-xl text-sm font-sans leading-relaxed text-left">
          {message.content}
        </div>

        {/* Attachment Chips */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="flex items-center justify-end flex-wrap gap-1.5 pt-1">
            {message.attachments.map((att) => (
              <div key={att.id} className="px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-300 flex items-center space-x-1">
                <Paperclip className="w-3 h-3 text-slate-400" />
                <span className="truncate max-w-[150px]">{att.name}</span>
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className="text-[10px] font-mono text-slate-500 flex items-center justify-end space-x-1">
          <Clock className="w-3 h-3" />
          <span>{message.timestamp}</span>
        </div>
      </div>

      <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1">
        <User className="w-4 h-4" />
      </div>
    </div>
  );
};

export default UserMessage;
