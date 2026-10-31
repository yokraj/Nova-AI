import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Sparkles,
  Search,
  Bell,
  Sun,
  Moon,
  ChevronDown,
  Menu,
} from 'lucide-react';
import { useThemeStore } from '@/stores/useThemeStore';
import { useAuthStore } from '@/stores/useAuthStore';

interface TopNavigationProps {
  onToggleRightPanel?: () => void;
  onToggleMobileMenu?: () => void;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  onToggleRightPanel,
  onToggleMobileMenu,
}) => {
  const { theme, toggleTheme } = useThemeStore();
  const { user } = useAuthStore();
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b border-zinc-800/80 bg-black/95 backdrop-blur-2xl px-3 sm:px-4 flex items-center justify-between z-30 sticky top-0 min-w-0 select-none">
      {/* Brand & Workspace & Mobile Hamburger */}
      <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
        {/* Mobile Hamburger Toggle */}
        <button
          onClick={onToggleMobileMenu}
          className="p-2 rounded-xl bg-zinc-900 border border-zinc-800 text-slate-400 hover:text-cyan-300 md:hidden cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-400"
          title="Open Navigation Menu"
          aria-label="Open menu"
        >
          <Menu className="w-4 h-4" />
        </button>

        <NavLink to="/" className="flex items-center space-x-2 sm:space-x-2.5 group">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 group-hover:shadow-[0_0_15px_rgba(0,240,255,0.4)] transition-all shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-extrabold text-base tracking-wider bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            NOVA<span className="text-slate-400 font-normal text-xs ml-1 font-mono">OS</span>
          </span>
        </NavLink>

        <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-zinc-900/90 border border-zinc-800 text-xs font-medium text-slate-300">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span>Workspace: <strong className="text-cyan-300 font-mono">Nova</strong></span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
        </div>
      </div>

      {/* Global Search Bar */}
      <div className="hidden md:flex items-center justify-center flex-1 px-4 min-w-0 max-w-md">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search OS memories, repos, skills, missions..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-zinc-900/90 border border-zinc-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all font-sans"
            readOnly
            aria-label="Search system"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] font-mono bg-zinc-800 text-slate-400 px-1.5 py-0.5 rounded">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Right Actions & Status */}
      <div className="flex items-center space-x-2 sm:space-x-2.5 shrink-0">
        {/* Live Clock */}
        <div className="hidden lg:block font-mono text-xs text-slate-400 px-2.5 py-1 bg-zinc-900/80 rounded-lg border border-zinc-800">
          {timeStr}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl bg-zinc-900 border border-zinc-800 text-slate-400 hover:text-cyan-300 hover:border-zinc-700 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-400"
          title="Toggle Theme"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Inspection Panel Toggle */}
        <button
          onClick={onToggleRightPanel}
          className="p-2 rounded-xl bg-zinc-900 border border-zinc-800 text-slate-400 hover:text-cyan-300 hover:border-zinc-700 transition-colors relative cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-400"
          title="Toggle Inspection Panel"
          aria-label="Toggle inspection panel"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-cyan-400 rounded-full shadow-[0_0_6px_rgba(0,240,255,0.8)]" />
        </button>

        {/* User Profile Avatar */}
        <div className="flex items-center space-x-2 pl-2 border-l border-zinc-800">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 font-bold text-xs shadow-md">
            {user?.name?.charAt(0) || 'A'}
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopNavigation;
