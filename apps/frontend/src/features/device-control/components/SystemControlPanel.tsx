import React from 'react';
import { Monitor, Lock, RefreshCw, Camera, Wifi } from 'lucide-react';
import { cn } from '@/utils/cn';

interface SystemControlPanelProps {
  onExecuteCommand: (cmd: string) => void;
  className?: string;
}

export const SystemControlPanel: React.FC<SystemControlPanelProps> = ({
  onExecuteCommand,
  className,
}) => {
  const actions = [
    { label: 'Take Screenshot', cmd: 'Take a screenshot', icon: Camera },
    { label: 'Turn on Wi-Fi', cmd: 'Turn on Wi-Fi', icon: Wifi },
    { label: 'Lock Computer', cmd: 'Lock my PC', icon: Lock },
    { label: 'Restart Computer', cmd: 'Restart my PC', icon: RefreshCw },
  ];

  return (
    <div className={cn('p-5 rounded-3xl bg-slate-950 border border-slate-800 space-y-4 shadow-2xl font-mono text-xs', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
          <Monitor className="w-4 h-4 text-cyan-400" />
          <span className="uppercase tracking-wider">SYSTEM CONTROL PANEL</span>
        </div>
        <span className="text-[10px] text-slate-500">Host OS</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {actions.map((act, idx) => {
          const Icon = act.icon;
          return (
            <button
              key={idx}
              onClick={() => onExecuteCommand(act.cmd)}
              className="p-3 rounded-2xl bg-slate-900 border border-slate-800 hover:border-cyan-500/40 text-slate-200 hover:text-cyan-300 font-bold transition-all cursor-pointer flex flex-col items-center justify-center space-y-1.5 text-center"
            >
              <Icon className="w-4 h-4 text-cyan-400" />
              <span className="text-[11px] font-sans">{act.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default SystemControlPanel;
