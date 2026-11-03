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
    <footer className="h-6 border-t border-cyan-500/20 bg-[#02040a]/90 backdrop-blur-2xl px-4 flex items-center justify-between text-[10px] font-mono text-slate-400 z-30 select-none min-w-0 w-full flex-shrink-0">
      {/* Left Items */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        <div className="flex items-center space-x-1.5 text-cyan-300">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          <span className="font-bold">NOVA_SYS_ONLINE</span>
          <span className="text-slate-500 hidden sm:inline">(Local 127.0.0.1)</span>
        </div>

        <div className="hidden sm:flex items-center space-x-1 text-slate-400">
          <Layers className="w-3 h-3 text-cyan-400" />
          <span>Workspace: <strong className="text-cyan-300 font-bold">Nova</strong></span>
        </div>

        <div className="hidden md:flex items-center space-x-1 text-slate-400">
          <ShieldCheck className="w-3 h-3 text-emerald-400" />
          <span>Security: <strong className="text-emerald-400">Restricted Local Guard</strong></span>
        </div>
      </div>

      {/* Right Items */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        <div className="hidden lg:flex items-center space-x-1 text-slate-400">
          <Cpu className="w-3 h-3 text-purple-400" />
          <span>NATIVE_BRIDGE: <strong className="text-cyan-300">ACTIVE:3001</strong></span>
        </div>

        <div className="flex items-center space-x-1 text-cyan-300 font-bold">
          <Zap className="w-3 h-3 text-cyan-400" />
          <span>{APP_CONFIG.name} <span className="text-slate-500 font-normal">v{APP_CONFIG.version}</span></span>
        </div>

        <div className="text-slate-500 font-mono">{timeStr}</div>
      </div>
    </footer>
  );
};

export default StatusBar;
