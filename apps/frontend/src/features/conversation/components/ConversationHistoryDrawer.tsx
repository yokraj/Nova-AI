import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Search, MessageSquare, Trash2, Edit2, Plus, Clock } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ConversationItem } from '../types/conversation';

interface ConversationHistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  conversations: ConversationItem[];
  activeId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation: (id: string, newTitle: string) => void;
  className?: string;
}

export const ConversationHistoryDrawer: React.FC<ConversationHistoryDrawerProps> = ({
  isOpen,
  onClose,
  conversations,
  activeId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  onRenameConversation,
  className,
}) => {
  const [search, setSearch] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  if (!isOpen) return null;

  const filtered = conversations.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  const startRename = (id: string, title: string) => {
    setEditingId(id);
    setEditTitle(title);
  };

  const saveRename = (id: string) => {
    if (editTitle.trim()) {
      onRenameConversation(id, editTitle);
    }
    setEditingId(null);
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex justify-start"
        onClick={onClose}
      >
        <motion.div
          initial={{ x: '-100%' }}
          animate={{ x: 0 }}
          exit={{ x: '-100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          onClick={(e) => e.stopPropagation()}
          className={cn('w-full max-w-sm h-full bg-slate-950 border-r border-slate-800 p-5 flex flex-col space-y-4 shadow-2xl font-mono text-xs', className)}
        >
          {/* Drawer Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
              <MessageSquare className="w-4 h-4 text-cyan-400" />
              <span className="uppercase tracking-wider">Conversation History</span>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* New Chat & Search Bar */}
          <button
            onClick={() => {
              onNewChat();
              onClose();
            }}
            className="w-full py-2.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center justify-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>+ Start New Chat</span>
          </button>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search conversations..."
              className="w-full bg-slate-900 border border-slate-800 rounded-xl py-2 pl-9 pr-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {filtered.length === 0 ? (
              <div className="text-center py-8 text-slate-500 font-sans text-xs">No conversations found</div>
            ) : (
              filtered.map((item) => {
                const isActive = item.id === activeId;
                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      onSelectConversation(item.id);
                      onClose();
                    }}
                    className={cn(
                      'p-3 rounded-xl border transition-all cursor-pointer space-y-1 group relative',
                      isActive
                        ? 'bg-cyan-500/10 border-cyan-500/50 text-cyan-300 shadow-[0_0_12px_rgba(0,240,255,0.15)]'
                        : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 text-slate-300'
                    )}
                  >
                    {editingId === item.id ? (
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && saveRename(item.id)}
                        className="w-full bg-slate-950 border border-cyan-500 px-2 py-1 rounded text-xs text-slate-100"
                        autoFocus
                      />
                    ) : (
                      <div className="flex items-center justify-between">
                        <span className="font-bold truncate text-slate-200">{item.title}</span>
                        <div className="hidden group-hover:flex items-center space-x-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              startRename(item.id, item.title);
                            }}
                            className="p-1 text-slate-400 hover:text-cyan-300"
                            title="Rename"
                          >
                            <Edit2 className="w-3 h-3" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onDeleteConversation(item.id);
                            }}
                            className="p-1 text-slate-400 hover:text-rose-400"
                            title="Delete"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-slate-600" />
                        <span>{item.updatedAt}</span>
                      </span>
                      <span>{item.messageCount} msgs</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ConversationHistoryDrawer;
