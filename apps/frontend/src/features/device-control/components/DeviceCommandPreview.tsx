import React from 'react';
import { Play, Terminal } from 'lucide-react';
import { cn } from '@/utils/cn';
import { DeviceActionRequest } from '../types/deviceAction';

interface DeviceCommandPreviewProps {
  action: DeviceActionRequest;
  onExecute: () => void;
  className?: string;
}

export const DeviceCommandPreview: React.FC<DeviceCommandPreviewProps> = ({
  action,
  onExecute,
  className,
}) => {
  const riskBadgeStyles = {
    SAFE: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    LOW: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    MEDIUM: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    HIGH: 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold',
    CRITICAL: 'bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold',
  };

  return (
    <div className={cn('p-4.5 rounded-3xl bg-slate-950 border border-cyan-500/40 space-y-3 font-mono text-xs shadow-2xl', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="uppercase tracking-wider">UNIVERSAL COMMAND PREVIEW</span>
        </div>
        <span className={cn('px-2 py-0.5 rounded-full text-[10px] border uppercase', riskBadgeStyles[action.riskLevel])}>
          Risk: {action.riskLevel}
        </span>
      </div>

      <div className="space-y-1">
        <div className="text-[10px] text-slate-400 uppercase font-bold">User Command</div>
        <div className="text-sm font-bold font-sans text-slate-100">"{action.commandText}"</div>
      </div>

      {/* Target & Pipeline Details */}
      <div className="grid grid-cols-2 gap-2 text-[11px]">
        <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-slate-500 block text-[10px]">Target Device</span>
          <span className="font-bold text-slate-200">{action.targetDeviceName}</span>
        </div>

        <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-slate-500 block text-[10px]">Required Capability</span>
          <span className="font-bold text-purple-300">{action.capabilityRequired}</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-1">
        <div className="text-[10px] text-slate-400">Policy: <strong className="text-cyan-300">{action.policy}</strong></div>
        <button
          onClick={onExecute}
          className="px-4 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1.5"
        >
          <Play className="w-4 h-4" />
          <span>Execute Command</span>
        </button>
      </div>
    </div>
  );
};

export default DeviceCommandPreview;
