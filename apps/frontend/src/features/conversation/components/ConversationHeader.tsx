import React from 'react';
import { Plus, History } from 'lucide-react';
import { cn } from '@/utils/cn';
import novaCoreImg from '@/assets/nova-core.png';

interface ConversationHeaderProps {
  title: string;
  onNewChat: () => void;
  onToggleHistory: () => void;
  className?: string;
}

export const ConversationHeader: React.FC<ConversationHeaderProps> = ({
  title,
  onNewChat,
  onToggleHistory,
  className,
}) => {
  return (
    <div className={cn('flex items-center justify-between px-6 py-3.5 bg-slate-950/90 border-b border-slate-800 text-xs font-mono sticky top-0 z-30 backdrop-blur-md', className)}>
      <div className="flex items-center space-x-3">
        {/* Nova Core Identity Indicator */}
        <div className="w-7 h-7 rounded-full overflow-hidden border border-cyan-400 shadow-[0_0_12px_rgba(0,240,255,0.4)] shrink-0">
          <img src={novaCoreImg} alt="Nova Core" className="w-full h-full object-cover" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-extrabold text-slate-100 truncate max-w-xs">{title}</span>
            <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[10px]">
              ONLINE
            </span>
          </div>
          <div className="text-[10px] text-slate-500 font-sans">Nova Universal Intelligence • Local-First</div>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={onToggleHistory}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-300 hover:border-cyan-500/30 transition-all cursor-pointer flex items-center space-x-1.5"
          title="Conversation History"
        >
          <History className="w-4 h-4" />
          <span className="hidden sm:inline">History</span>
        </button>

        <button
          onClick={onNewChat}
          className="px-3 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1.5"
          title="New Conversation"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">New Chat</span>
        </button>
      </div>
    </div>
  );
};

export default ConversationHeader;
