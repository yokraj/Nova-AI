import React, { useState, useEffect } from 'react';
import { Sparkles, Calendar, Clock, FolderGit2, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { cn } from '@/utils/cn';
import { useDashboardData } from '@/hooks/useDashboardData';

export interface NovaHeaderProps {
  className?: string;
  isConnected?: boolean;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const NovaHeader: React.FC<NovaHeaderProps> = ({
  className,
  isConnected: externalIsConnected,
  onRefresh,
  isRefreshing: externalIsRefreshing,
}) => {
  const [timeString, setTimeString] = useState<string>('');
  const [dateString, setDateString] = useState<string>('');

  // Auto-connect to live dashboard context if props are omitted
  const {
    data: dashboardData,
    connectionStatus,
    isRefreshing: hookIsRefreshing,
    refresh: hookRefresh,
  } = useDashboardData();

  const isConnected =
    externalIsConnected !== undefined
      ? externalIsConnected
      : connectionStatus === 'connected' && !!dashboardData?.isConnected;

  const isRefreshing =
    externalIsRefreshing !== undefined ? externalIsRefreshing : hookIsRefreshing;

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      hookRefresh(true);
    }
  };

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeString(
        now.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        })
      );
      setDateString(
        now.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header
      className={cn(
        'glass-panel p-4 sm:p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl select-none',
        className
      )}
    >
      {/* Left: Branding & Tagline */}
      <div className="flex items-center space-x-3.5">
        <div className="p-2.5 sm:p-3 bg-gradient-to-br from-cyan-500/20 via-blue-600/20 to-purple-600/20 rounded-2xl border border-cyan-500/30 text-cyan-300 shadow-[0_0_20px_rgba(0,240,255,0.2)] shrink-0">
          <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 animate-pulse text-cyan-400" />
        </div>
        <div>
          <div className="flex items-center space-x-2 flex-wrap">
            <h1 className="text-xl sm:text-2xl font-black tracking-tight text-slate-100 font-sans">
              NOVA
            </h1>
            <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 uppercase tracking-wider">
              AI OS v3.5
            </span>
            <span
              className={cn(
                'hidden sm:inline-block text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border uppercase',
                isConnected
                  ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                  : 'bg-slate-800/80 text-slate-400 border-slate-700/80'
              )}
            >
              {isConnected ? 'LIVE CONNECTED' : 'STANDALONE MODE'}
            </span>
          </div>
          <p className="text-xs font-mono text-slate-400 tracking-wide mt-0.5">
            Universal Intelligence Operating System • Command Center
          </p>
        </div>
      </div>

      {/* Right: Workspace, Date/Time, Refresh, and Live Connectivity */}
      <div className="flex items-center flex-wrap gap-2 sm:gap-3 text-xs font-mono">
        {/* Workspace Pill */}
        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300">
          <FolderGit2 className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Workspace:</span>
          <strong className="text-slate-100 font-bold">Nova-AI</strong>
        </div>

        {/* Date & Time Pill */}
        <div className="hidden sm:flex items-center space-x-2.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300">
          <span className="flex items-center space-x-1 text-slate-400">
            <Calendar className="w-3.5 h-3.5 text-purple-400" />
            <span>{dateString || 'Current Date'}</span>
          </span>
          <span className="text-slate-600">•</span>
          <span className="flex items-center space-x-1 text-cyan-300 font-bold">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>{timeString || '00:00:00'}</span>
          </span>
        </div>

        {/* Refresh Action Button */}
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
          title="Refresh System Telemetry"
          aria-label="Refresh telemetry"
        >
          <RefreshCw className={cn('w-3.5 h-3.5', isRefreshing && 'animate-spin text-cyan-400')} />
        </button>

        {/* System Online / Offline Status Pill */}
        <div
          className={cn(
            'flex items-center space-x-2 px-3 py-1.5 rounded-xl border text-xs font-bold tracking-wider transition-all',
            isConnected
              ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.15)]'
              : 'bg-slate-800/80 border-slate-700/80 text-slate-400'
          )}
        >
          {isConnected ? (
            <>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <Wifi className="w-3.5 h-3.5 text-emerald-400" />
              <span>CORE ONLINE</span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 rounded-full border border-slate-400" />
              <WifiOff className="w-3.5 h-3.5 text-slate-400" />
              <span>STANDALONE LOCAL</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default NovaHeader;
