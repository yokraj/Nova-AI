import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  MessageSquare,
  Monitor,
  Bot,
  Brain,
  Cpu,
  BarChart3,
  Settings,
  ChevronRight,
  ChevronLeft,
  X,
  Layers,
  Terminal,
  Rocket,
  Zap,
  BookOpen,
  FolderGit2,
  Mic,
  Clock,
} from 'lucide-react';
import { cn } from '@/utils/cn';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

interface RailItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  exact?: boolean;
  badge?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  onToggleCollapse,
  mobileOpen = false,
  onCloseMobile,
}) => {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  // 8 Primary Navigation Rail Items required by JARVIS OS directive
  const primaryRailItems: RailItem[] = [
    { to: '/', label: 'Home', icon: Sparkles, exact: true },
    { to: '/chat', label: 'Intelligence / Chat', icon: MessageSquare, badge: 'AI' },
    { to: '/computer-control', label: 'Applications', icon: Monitor },
    { to: '/agents', label: 'Agents', icon: Bot, badge: 'Auto' },
    { to: '/memory', label: 'Memory', icon: Brain },
    { to: '/devices', label: 'Devices', icon: Cpu },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  // Secondary capabilities preserved in expandable section or mobile drawer
  const secondaryItems: RailItem[] = [
    { to: '/mission-control', label: 'Missions', icon: Rocket },
    { to: '/skills', label: 'Skills', icon: Zap },
    { to: '/workflows', label: 'Workflows', icon: Layers },
    { to: '/terminal', label: 'Terminal', icon: Terminal },
    { to: '/voice', label: 'Voice Center', icon: Mic },
    { to: '/knowledge', label: 'Knowledge Graph', icon: BookOpen },
    { to: '/repositories', label: 'Repositories', icon: FolderGit2 },
    { to: '/automation', label: 'Automation', icon: Clock },
  ];

  const renderNavList = (items: RailItem[], isMobile = false) => (
    <div className="space-y-1.5 w-full flex flex-col items-center">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <div
            key={item.to}
            className="relative w-full flex justify-center"
            onMouseEnter={() => !isMobile && setHoveredItem(item.label)}
            onMouseLeave={() => !isMobile && setHoveredItem(null)}
          >
            <NavLink
              to={item.to}
              end={item.exact}
              onClick={isMobile ? onCloseMobile : undefined}
              className={({ isActive }) =>
                cn(
                  'w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-200 relative group cursor-pointer',
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/50 shadow-[0_0_15px_rgba(0,240,255,0.3)]'
                    : 'text-slate-400 hover:text-cyan-300 hover:bg-slate-900/80 border border-transparent hover:border-cyan-500/30'
                )
              }
              aria-label={item.label}
            >
              {({ isActive }) => (
                <>
                  <Icon className={cn('w-5 h-5 transition-transform group-hover:scale-110', isActive && 'text-cyan-300')} />
                  
                  {/* Left Active Glow Beam */}
                  {isActive && (
                    <span className="absolute -left-2 top-1.5 bottom-1.5 w-1 bg-cyan-400 rounded-r shadow-[0_0_8px_#00f0ff]" />
                  )}

                  {/* Optional Micro Badge */}
                  {item.badge && !isActive && (
                    <span className="absolute -top-1 -right-1 text-[8px] font-mono px-1 py-0.2 bg-cyan-950 text-cyan-400 rounded border border-cyan-500/40">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </NavLink>

            {/* Futuristic Holographic Hover Tooltip for Rail */}
            {!isMobile && hoveredItem === item.label && (
              <div className="absolute left-14 top-1/2 -translate-y-1/2 z-50 pointer-events-none whitespace-nowrap">
                <motion.div
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="px-2.5 py-1 rounded-lg bg-slate-950/95 border border-cyan-500/40 text-cyan-300 text-xs font-mono tracking-wider shadow-[0_0_15px_rgba(0,0,0,0.8),0_0_10px_rgba(0,240,255,0.2)] flex items-center space-x-1.5"
                >
                  <span className="w-1 h-1 rounded-full bg-cyan-400 animate-ping" />
                  <span>{item.label}</span>
                </motion.div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );

  return (
    <>
      {/* 1. Desktop Slim Icon Rail */}
      <aside className="hidden md:flex flex-col items-center justify-between py-4 w-16 border-r border-cyan-500/20 bg-[#02040a]/90 backdrop-blur-2xl z-20 shrink-0 min-h-[calc(100vh-3.5rem)] select-none">
        {/* Top Primary Icons */}
        <div className="w-full flex flex-col items-center space-y-4">
          <div className="w-6 h-[1px] bg-cyan-500/30 mb-1" />
          {renderNavList(primaryRailItems)}
        </div>

        {/* Bottom Tool Link / Subsystems Toggle */}
        <div className="w-full flex flex-col items-center space-y-3 pt-3 border-t border-cyan-500/20">
          <NavLink
            to="/workflows"
            title="Advanced Workspaces & Subsystems"
            className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-400 hover:text-cyan-300 hover:bg-slate-900 border border-transparent hover:border-cyan-500/30 transition-all cursor-pointer"
          >
            <Layers className="w-4 h-4 text-cyan-400/80" />
          </NavLink>
        </div>
      </aside>

      {/* 2. Mobile Drawer with Complete Navigation List */}
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
              className="relative w-72 max-w-[85vw] h-full bg-[#02040a] border-r border-cyan-500/30 shadow-2xl flex flex-col z-10 p-4 overflow-y-auto"
            >
              {/* Drawer Header */}
              <div className="pb-4 border-b border-cyan-500/20 flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/40">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <span className="font-mono font-bold text-cyan-300 text-sm tracking-wider">
                    NOVA OS NAVIGATION
                  </span>
                </div>
                <button
                  onClick={onCloseMobile}
                  className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 cursor-pointer"
                  aria-label="Close menu"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Primary Rail Links in Mobile */}
              <div className="space-y-1 mb-6">
                <span className="text-[10px] font-mono tracking-widest text-cyan-400/70 uppercase px-2 mb-1 block">
                  Core Subsystems
                </span>
                {primaryRailItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.exact}
                      onClick={onCloseMobile}
                      className={({ isActive }) =>
                        cn(
                          'flex items-center space-x-3 px-3 py-2 rounded-xl text-xs font-mono tracking-wider transition-all cursor-pointer',
                          isActive
                            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                        )
                      }
                    >
                      <Icon className="w-4 h-4 text-cyan-400" />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </div>

              {/* Secondary Subsystem Links */}
              <div className="space-y-1 border-t border-cyan-500/20 pt-4">
                <span className="text-[10px] font-mono tracking-widest text-cyan-400/70 uppercase px-2 mb-1 block">
                  Advanced Workspaces
                </span>
                {secondaryItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      onClick={onCloseMobile}
                      className={({ isActive }) =>
                        cn(
                          'flex items-center space-x-3 px-3 py-2 rounded-xl text-xs font-mono tracking-wider transition-all cursor-pointer',
                          isActive
                            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                        )
                      }
                    >
                      <Icon className="w-4 h-4 text-cyan-400/80" />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Sidebar;
