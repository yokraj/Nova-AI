import React from 'react';
import { Lightbulb, Tv, Power } from 'lucide-react';
import { cn } from '@/utils/cn';

interface SmartDevicePanelProps {
  onExecuteCommand: (cmd: string) => void;
  className?: string;
}

export const SmartDevicePanel: React.FC<SmartDevicePanelProps> = ({
  onExecuteCommand,
  className,
}) => {
  return (
    <div className={cn('p-5 rounded-3xl bg-slate-950 border border-slate-800 space-y-4 shadow-2xl font-mono text-xs', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2 text-amber-300 font-extrabold">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          <span className="uppercase tracking-wider">SMART HOME CONTROL PANEL</span>
        </div>
        <span className="text-[10px] text-slate-500">Local Zigbee Subnet</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-100 font-sans text-xs">Bedroom Smart Light</span>
            <span className="text-emerald-400 text-[10px] font-bold">ONLINE</span>
          </div>
          <button
            onClick={() => onExecuteCommand('Turn on bedroom light')}
            className="w-full py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-[11px] font-bold transition-all cursor-pointer flex items-center justify-center space-x-1"
          >
            <Power className="w-3.5 h-3.5" />
            <span>Toggle Light Power</span>
          </button>
        </div>

        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-100 font-sans text-xs">Living Room TV</span>
            <span className="text-slate-500 text-[10px] font-bold">OFFLINE</span>
          </div>
          <button
            onClick={() => onExecuteCommand('Turn on Living Room TV')}
            className="w-full py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] font-bold transition-all cursor-pointer flex items-center justify-center space-x-1"
          >
            <Tv className="w-3.5 h-3.5" />
            <span>Wake Smart TV</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SmartDevicePanel;
