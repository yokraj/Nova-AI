import React, { useState, useEffect } from 'react';
import { Cpu, Layers, ShieldCheck, Zap } from 'lucide-react';
import { APP_CONFIG } from '@/config/app.config';

export const StatusBar: React.FC = () => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <footer className="h-7 border-t border-zinc-800/80 bg-black/95 backdrop-blur-2xl px-4 flex items-center justify-between text-[11px] font-mono text-slate-400 z-30 select-none min-w-0 w-full flex-shrink-0">
      {/* Left Items */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5 text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
          <span className="font-bold">SYSTEM ACTIVE</span>
          <span className="text-slate-500">(Local 127.0.0.1)</span>
        </div>

        <div className="hidden sm:flex items-center space-x-1 text-slate-400">
          <Layers className="w-3 h-3 text-cyan-400" />
          <span>Workspace: <strong className="text-slate-200">Nova</strong></span>
        </div>

        <div className="hidden md:flex items-center space-x-1 text-slate-400">
          <ShieldCheck className="w-3 h-3 text-blue-400" />
          <span>Mode: <strong className="text-slate-200">Zero-Cost Local</strong></span>
        </div>
      </div>

      {/* Right Items */}
      <div className="flex items-center space-x-4">
        <div className="hidden lg:flex items-center space-x-1 text-slate-400">
          <Cpu className="w-3 h-3 text-purple-400" />
          <span>CPU: <strong className="text-slate-200">18.2%</strong> | RAM: <strong className="text-slate-200">3.8GB</strong></span>
        </div>

        <div className="flex items-center space-x-1 text-cyan-300">
          <Zap className="w-3 h-3 text-cyan-400" />
          <span>{APP_CONFIG.name} <span className="text-slate-500">v{APP_CONFIG.version}</span></span>
        </div>

        <div>{timeStr}</div>
      </div>
    </footer>
  );
};

export default StatusBar;
