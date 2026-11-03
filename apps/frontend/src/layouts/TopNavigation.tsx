import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Sparkles,
  Terminal,
  Layers,
  Bot,
  Brain,
  Monitor,
  Search,
  Bell,
  Sun,
  Moon,
  ChevronDown,
  Menu,
  Activity,
  ShieldCheck,
} from 'lucide-react';
import { useThemeStore } from '@/stores/useThemeStore';
import { useAuthStore } from '@/stores/useAuthStore';
import { cn } from '@/utils/cn';

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
  const [dateStr, setDateStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
      setDateStr(now.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' }).toUpperCase());
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { to: '/', label: 'Command', icon: Terminal, exact: true },
    { to: '/workflows', label: 'Workspace', icon: Layers },
    { to: '/agents', label: 'Agents', icon: Bot },
    { to: '/memory', label: 'Memory', icon: Brain },
    { to: '/devices', label: 'Devices', icon: Monitor },
  ];

  return (
    <header className="h-14 border-b border-cyan-500/20 bg-[#02040a]/90 backdrop-blur-2xl px-3 sm:px-6 flex items-center justify-between z-30 sticky top-0 min-w-0 select-none shadow-[0_4px_30px_rgba(0,0,0,0.8)]">
      {/* Brand & Identity */}
      <div className="flex items-center space-x-3 sm:space-x-5 shrink-0">
        {/* Mobile Hamburger Toggle */}
        <button
          onClick={onToggleMobileMenu}
          className="p-1.5 rounded-lg bg-slate-900/80 border border-cyan-500/30 text-slate-400 hover:text-cyan-300 md:hidden cursor-pointer focus:outline-none focus:ring-1 focus:ring-cyan-400"
          title="Open Navigation Menu"
          aria-label="Open menu"
        >
          <Menu className="w-4 h-4" />
        </button>

        {/* NOVA OS Logo with Holographic Arc */}
        <NavLink to="/" className="flex items-center space-x-2.5 group">
          <div className="relative p-1.5 rounded-xl bg-cyan-500/10 border border-cyan-400/40 text-cyan-400 group-hover:border-cyan-300 group-hover:shadow-[0_0_20px_rgba(0,240,255,0.6)] transition-all shrink-0">
            <Sparkles className="w-4 h-4 animate-pulse" />
            <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00f0ff]" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center space-x-1">
              <span className="font-extrabold text-sm tracking-widest bg-gradient-to-r from-cyan-300 via-sky-400 to-blue-500 bg-clip-text text-transparent group-hover:drop-shadow-[0_0_8px_rgba(0,240,255,0.7)] transition-all">
                NOVA
              </span>
              <span className="text-[10px] font-mono tracking-wider text-cyan-400/90 font-bold px-1 py-0.2 bg-cyan-500/10 rounded border border-cyan-500/30">
                OS
              </span>
            </div>
            <span className="text-[9px] font-mono tracking-widest text-slate-500 uppercase -mt-0.5 hidden sm:inline">
              JARVIS ARCHITECTURE
            </span>
          </div>
        </NavLink>

        {/* System Online Status Indicator */}
        <div className="hidden xl:flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-[10px] font-mono text-cyan-300">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 -ml-2" />
          <span>SYS_ONLINE</span>
          <span className="text-slate-500">|</span>
          <span className="text-emerald-400 flex items-center space-x-0.5">
            <ShieldCheck className="w-3 h-3 inline" />
            <span>SECURE</span>
          </span>
        </div>
      </div>

      {/* Central Top Navigation Links (Command, Workspace, Agents, Memory, Devices) */}
      <nav className="hidden md:flex items-center space-x-1 lg:space-x-2 shrink-0">
        {navLinks.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.exact}
              className={({ isActive }) =>
                cn(
                  'px-3 py-1.5 rounded-lg text-xs font-mono tracking-wider flex items-center space-x-1.5 transition-all relative group cursor-pointer',
                  isActive
                    ? 'text-cyan-300 bg-cyan-500/15 border border-cyan-500/40 shadow-[0_0_15px_rgba(0,240,255,0.2)] font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={cn('w-3.5 h-3.5 transition-colors', isActive ? 'text-cyan-300' : 'text-slate-500 group-hover:text-cyan-400')} />
                  <span>{link.label}</span>
                  {isActive && (
                    <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-cyan-400 rounded-full shadow-[0_0_8px_#00f0ff]" />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Right Search, Live Date/Time, Notifications & User */}
      <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
        {/* Compact Search Trigger */}
        <div className="hidden lg:flex items-center relative">
          <div className="flex items-center space-x-2 pl-3 pr-2 py-1 rounded-xl bg-slate-950/80 border border-cyan-500/20 text-xs text-slate-400 hover:border-cyan-500/40 hover:text-slate-200 transition-all cursor-pointer">
            <Search className="w-3.5 h-3.5 text-cyan-400/80" />
            <span className="text-[11px] font-mono text-slate-400 pr-3">Search Nova OS...</span>
            <kbd className="text-[9px] font-mono bg-cyan-950/60 text-cyan-300 px-1.5 py-0.5 rounded border border-cyan-500/30">
              ⌘K
            </kbd>
          </div>
        </div>

        {/* Live HUD Date & Clock */}
        <div className="hidden sm:flex flex-col items-end px-2.5 py-1 bg-slate-950/60 rounded-lg border border-cyan-500/20 text-right">
          <span className="font-mono text-[11px] font-bold text-cyan-300 tracking-wider">
            {timeStr || '00:00:00'}
          </span>
          <span className="font-mono text-[9px] text-slate-400 tracking-widest -mt-0.5">
            {dateStr || 'SYSTEM'}
          </span>
        </div>

        {/* Right Panel / Notifications HUD Toggle */}
        <button
          onClick={onToggleRightPanel}
          className="p-1.5 sm:p-2 rounded-xl bg-slate-950/80 border border-cyan-500/25 text-slate-400 hover:text-cyan-300 hover:border-cyan-400/50 hover:shadow-[0_0_15px_rgba(0,240,255,0.25)] transition-all relative cursor-pointer focus:outline-none"
          title="Toggle System Context Panel"
          aria-label="Toggle system context panel"
        >
          <Bell className="w-4 h-4 text-cyan-400/90" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-cyan-400 rounded-full shadow-[0_0_8px_rgba(0,240,255,0.9)] animate-pulse" />
        </button>

        {/* User Profile Avatar with Holographic Border */}
        <div className="flex items-center space-x-2 pl-1.5 border-l border-cyan-500/20">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-700 p-[1px] shadow-[0_0_12px_rgba(0,240,255,0.3)]">
            <div className="w-full h-full rounded-[11px] bg-[#02040a] flex items-center justify-center text-cyan-300 font-mono font-bold text-xs">
              {user?.name?.charAt(0) || 'C'}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopNavigation;
