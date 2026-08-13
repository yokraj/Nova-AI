import React, { useState, useEffect } from 'react';
import { Sparkles, Calendar, Clock, FolderGit2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { StatusBadge } from '@/components/status/StatusIndicators';

export const NovaHeader: React.FC<{ className?: string }> = ({ className }) => {
  const [timeString, setTimeString] = useState<string>('');
  const [dateString, setDateString] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeString(
        now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
      );
      setDateString(
        now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className={cn('glass-panel p-5 rounded-3xl border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl', className)}>
      <div className="flex items-center space-x-4">
        <div className="p-3 bg-gradient-to-br from-cyan-500/20 via-blue-600/20 to-purple-600/20 rounded-2xl border border-cyan-500/30 text-cyan-300 shadow-[0_0_20px_rgba(0,240,255,0.2)]">
          <Sparkles className="w-6 h-6 animate-pulse text-cyan-400" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-black tracking-tight text-slate-100 font-sans">NOVA</h1>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 uppercase">
              AI OS v3.4
            </span>
          </div>
          <p className="text-xs font-mono text-slate-400 tracking-wide">
            Universal Intelligence Operating System Command Center
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4 text-xs font-mono">
        {/* Workspace pill */}
        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300">
          <FolderGit2 className="w-3.5 h-3.5 text-cyan-400" />
          <span>Workspace: <strong className="text-slate-100 font-bold">Nova-AI</strong></span>
        </div>

        {/* Date & Time pill */}
        <div className="hidden sm:flex items-center space-x-3 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300">
          <span className="flex items-center space-x-1">
            <Calendar className="w-3.5 h-3.5 text-purple-400" />
            <span>{dateString || 'Aug 11, 2026'}</span>
          </span>
          <span className="text-slate-600">•</span>
          <span className="flex items-center space-x-1 text-cyan-300 font-bold">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>{timeString || '22:30:00'}</span>
          </span>
        </div>

        {/* System Status pill */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="font-bold tracking-wider">ONLINE</span>
        </div>
      </div>
    </header>
  );
};

export default NovaHeader;
