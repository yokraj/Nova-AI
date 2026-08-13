import React from 'react';
import { motion } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Pin,
  Folder,
  MessageSquare,
  Star,
  Layers,
  Sparkles,
  Zap,
} from 'lucide-react';
import { NavigationItem } from './NavigationItem';
import { SidebarSection } from './SidebarSection';
import { cn } from '@/utils/cn';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggleCollapse }) => {
  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 256 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className="h-[calc(100vh-4rem)] border-r border-slate-800/80 bg-slate-950/90 backdrop-blur-xl flex flex-col justify-between z-20 select-none flex-shrink-0"
    >
      {/* Upper Content */}
      <div className="p-3 space-y-4 overflow-y-auto no-scrollbar">
        {/* Quick Action Button */}
        <button
          className={cn(
            'w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-bold text-xs flex items-center justify-center space-x-2 shadow-[0_0_20px_rgba(0,240,255,0.25)] hover:shadow-[0_0_25px_rgba(0,240,255,0.4)] hover:scale-[1.02] transition-all',
            collapsed && 'px-0'
          )}
        >
          <Plus className="w-4 h-4" />
          {!collapsed && <span>New Execution</span>}
        </button>

        {/* Section: Quick Nav */}
        <SidebarSection title="Nav" collapsed={collapsed}>
          <NavigationItem to="/" icon={Sparkles} label="Overview" collapsed={collapsed} />
          <NavigationItem to="/chat" icon={MessageSquare} label="Intelligence Chat" badge="3" collapsed={collapsed} />
          <NavigationItem to="/repositories" icon={Folder} label="Source Repos" collapsed={collapsed} />
        </SidebarSection>

        {/* Section: Pinned Chats */}
        <SidebarSection title="Pinned Chats" collapsed={collapsed}>
          <div className="space-y-1">
            <button className={cn('w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-cyan-300 hover:bg-slate-900/60 transition-colors text-left truncate', collapsed && 'justify-center px-0')}>
              <Pin className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
              {!collapsed && <span className="truncate">Nova Architecture Refactor</span>}
            </button>
            <button className={cn('w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-cyan-300 hover:bg-slate-900/60 transition-colors text-left truncate', collapsed && 'justify-center px-0')}>
              <Pin className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
              {!collapsed && <span className="truncate">Inference Gateway Benchmarks</span>}
            </button>
          </div>
        </SidebarSection>

        {/* Section: Projects */}
        <SidebarSection title="Projects" collapsed={collapsed}>
          <div className="space-y-1">
            <button className={cn('w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-cyan-300 hover:bg-slate-900/60 transition-colors text-left truncate', collapsed && 'justify-center px-0')}>
              <Folder className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
              {!collapsed && <span className="truncate">Kernel Subsystems</span>}
            </button>
            <button className={cn('w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-cyan-300 hover:bg-slate-900/60 transition-colors text-left truncate', collapsed && 'justify-center px-0')}>
              <Folder className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
              {!collapsed && <span className="truncate">AI Workforce Fleet</span>}
            </button>
          </div>
        </SidebarSection>

        {/* Section: Recent Conversations */}
        <SidebarSection title="Recent" collapsed={collapsed}>
          <div className="space-y-1">
            <button className={cn('w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 transition-colors text-left truncate', collapsed && 'justify-center px-0')}>
              <MessageSquare className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
              {!collapsed && <span className="truncate">Hybrid RAG Evaluation</span>}
            </button>
          </div>
        </SidebarSection>
      </div>

      {/* Footer Collapse Button */}
      <div className="p-3 border-t border-slate-800/80">
        <button
          onClick={onToggleCollapse}
          className="w-full flex items-center justify-center p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
