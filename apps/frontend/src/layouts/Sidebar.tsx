import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Sparkles,
  MessageSquare,
  Search,
  Mic,
  Rocket,
  Bot,
  Zap,
  Layers,
  Brain,
  BookOpen,
  FolderGit2,
  Globe,
  Monitor,
  Terminal,
  Clock,
  Cpu,
  BarChart3,
  Settings,
  X,
} from 'lucide-react';
import { NavigationItem } from './NavigationItem';
import { SidebarSection } from './SidebarSection';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  onToggleCollapse,
  mobileOpen = false,
  onCloseMobile,
}) => {
  const sidebarContent = (
    <div className="flex flex-col h-full justify-between select-none font-sans">
      {/* Upper Navigation Sections */}
      <div className="p-2.5 space-y-3 overflow-y-auto no-scrollbar flex-1">
        {/* PRIMARY: CORE INTELLIGENCE */}
        <SidebarSection title="PRIMARY INTELLIGENCE" collapsed={collapsed} defaultExpanded={true}>
          <NavigationItem to="/" icon={Sparkles} label="Nova Core" collapsed={collapsed} />
          <NavigationItem to="/chat" icon={MessageSquare} label="Intelligence Chat" badge="Live" collapsed={collapsed} />
          <NavigationItem to="/voice" icon={Mic} label="Voice Center" badge="Voice" collapsed={collapsed} />
          <NavigationItem to="/knowledge" icon={Search} label="Research Center" collapsed={collapsed} />
        </SidebarSection>

        {/* WORK: MISSIONS & AGENTS */}
        <SidebarSection title="WORK & WORKFORCE" collapsed={collapsed} defaultExpanded={true}>
          <NavigationItem to="/mission-control" icon={Rocket} label="Autonomous Missions" collapsed={collapsed} />
          <NavigationItem to="/agents" icon={Bot} label="Agent Workforce" badge="67" collapsed={collapsed} />
          <NavigationItem to="/skills" icon={Zap} label="Learned Skills" collapsed={collapsed} />
          <NavigationItem to="/workflows" icon={Layers} label="Workflow Studio" collapsed={collapsed} />
        </SidebarSection>

        {/* KNOWLEDGE & MEMORY */}
        <SidebarSection title="MEMORY & KNOWLEDGE" collapsed={collapsed} defaultExpanded={true}>
          <NavigationItem to="/memory" icon={Brain} label="Memory Center" badge="142k" collapsed={collapsed} />
          <NavigationItem to="/knowledge" icon={BookOpen} label="Knowledge Graph" collapsed={collapsed} />
          <NavigationItem to="/repositories" icon={FolderGit2} label="Repositories" collapsed={collapsed} />
        </SidebarSection>

        {/* CONTROL & EXECUTION */}
        <SidebarSection title="DESKTOP & DEVICE CONTROL" collapsed={collapsed} defaultExpanded={false}>
          <NavigationItem to="/devices" icon={Globe} label="Browser Automation" collapsed={collapsed} />
          <NavigationItem to="/computer-control" icon={Monitor} label="Computer Control" collapsed={collapsed} />
          <NavigationItem to="/terminal" icon={Terminal} label="System Control" collapsed={collapsed} />
          <NavigationItem to="/automation" icon={Clock} label="Background Automations" collapsed={collapsed} />
        </SidebarSection>

        {/* SYSTEM CONFIGURATION */}
        <SidebarSection title="SYSTEM & SETTINGS" collapsed={collapsed} defaultExpanded={false}>
          <NavigationItem to="/models" icon={Cpu} label="Local Models (Ollama)" collapsed={collapsed} />
          <NavigationItem to="/analytics" icon={BarChart3} label="Diagnostics & Health" collapsed={collapsed} />
          <NavigationItem to="/settings" icon={Settings} label="Settings" collapsed={collapsed} />
        </SidebarSection>
      </div>

      {/* Footer Collapse Button (Desktop Only) */}
      <div className="p-2 border-t border-zinc-800/80 hidden md:block">
        <button
          onClick={onToggleCollapse}
          className="w-full flex items-center justify-center p-2 rounded-xl bg-zinc-900/90 hover:bg-zinc-800 text-slate-400 hover:text-cyan-300 border border-zinc-800 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-400"
          title={collapsed ? 'Expand Navigation Sidebar' : 'Collapse Navigation Sidebar'}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* 1. Desktop Sidebar */}
      <motion.aside
        animate={{ width: collapsed ? 72 : 240 }}
        transition={{ duration: 0.2, ease: 'easeInOut' }}
        className="hidden md:flex flex-col h-[calc(100vh-4rem)] border-r border-zinc-800/80 bg-black/95 backdrop-blur-2xl z-20 shrink-0 min-w-0"
      >
        {sidebarContent}
      </motion.aside>

      {/* 2. Mobile Drawer with Backdrop Blur */}
      <AnimatePresence>
        {mobileOpen && (
          <div className="fixed inset-0 z-50 md:hidden flex">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onCloseMobile}
              className="fixed inset-0 bg-black/80 backdrop-blur-md"
            />

            {/* Slide-out Drawer */}
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 25, stiffness: 220 }}
              className="relative w-72 max-w-[85vw] h-full bg-slate-950 border-r border-slate-800 shadow-2xl flex flex-col z-10"
            >
              {/* Drawer Top Bar */}
              <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <span className="font-bold text-slate-100 text-sm font-mono tracking-wider">
                    NOVA NAVIGATION
                  </span>
                </div>
                <button
                  onClick={onCloseMobile}
                  className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-slate-400 hover:text-slate-100 cursor-pointer"
                  aria-label="Close menu"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Navigation Items */}
              <div className="flex-1 overflow-y-auto">{sidebarContent}</div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Sidebar;
