import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Sparkles,
  Search,
  Bell,
  Sun,
  Moon,
  ChevronDown,
  User,
  LayoutDashboard,
  MessageSquare,
  Brain,
  BookOpen,
  FolderGit2,
  Bot,
  Rocket,
  BarChart3,
  Cpu,
  Terminal,
  Mic,
  Settings,
  SlidersHorizontal,
} from 'lucide-react';
import { useThemeStore } from '@/stores/useThemeStore';
import { useAuthStore } from '@/stores/useAuthStore';
import { cn } from '@/utils/cn';

interface TopNavigationProps {
  onToggleRightPanel?: () => void;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({ onToggleRightPanel }) => {
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

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/chat', label: 'Chat', icon: MessageSquare },
    { to: '/memory', label: 'Memory', icon: Brain },
    { to: '/knowledge', label: 'Knowledge', icon: BookOpen },
    { to: '/repositories', label: 'Repos', icon: FolderGit2 },
    { to: '/agents', label: 'Agents', icon: Bot },
    { to: '/mission-control', label: 'Mission', icon: Rocket },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/models', label: 'Models', icon: Cpu },
    { to: '/terminal', label: 'Terminal', icon: Terminal },
    { to: '/voice', label: 'Voice', icon: Mic },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl px-4 flex items-center justify-between z-30 sticky top-0">
      {/* Brand & Workspace */}
      <div className="flex items-center space-x-4">
        <NavLink to="/" className="flex items-center space-x-2.5 group">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 group-hover:shadow-[0_0_15px_rgba(0,240,255,0.4)] transition-all">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-extrabold text-lg tracking-wider bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            NOVA<span className="text-slate-400 font-normal text-xs ml-1 font-mono">OS</span>
          </span>
        </NavLink>

        <div className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-medium text-slate-300">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span>Workspace: <strong className="text-cyan-300 font-mono">Nova</strong></span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
        </div>
      </div>

      {/* Primary Top Nav Tabs */}
      <nav className="hidden lg:flex items-center space-x-1 overflow-x-auto no-scrollbar py-1">
        {navLinks.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold shadow-[0_0_10px_rgba(0,240,255,0.1)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
                )
              }
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{link.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Global Search & Actions */}
      <div className="flex items-center space-x-3">
        {/* Global Search Placeholder */}
        <div className="relative hidden sm:block w-48 lg:w-64">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search OS memories, repos..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            readOnly
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] font-mono bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">
            ⌘K
          </kbd>
        </div>

        {/* Live Clock */}
        <div className="hidden xl:block font-mono text-xs text-slate-400 px-2 py-1 bg-slate-900/50 rounded-lg border border-slate-800">
          {timeStr}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 hover:border-slate-700 transition-colors"
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Notification Button */}
        <button
          onClick={onToggleRightPanel}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 hover:border-slate-700 transition-colors relative"
          title="Toggle Inspection Panel"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-cyan-400 rounded-full shadow-[0_0_6px_rgba(0,240,255,0.8)]" />
        </button>

        {/* User Profile Avatar */}
        <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 font-bold text-xs shadow-md">
            {user?.name?.charAt(0) || 'A'}
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopNavigation;
