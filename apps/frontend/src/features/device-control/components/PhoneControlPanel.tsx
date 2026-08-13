import React from 'react';
import { Smartphone, Phone, MessageSquare, Bell } from 'lucide-react';
import { cn } from '@/utils/cn';

interface PhoneControlPanelProps {
  onExecuteCommand: (cmd: string) => void;
  className?: string;
}

export const PhoneControlPanel: React.FC<PhoneControlPanelProps> = ({
  onExecuteCommand,
  className,
}) => {
  const actions = [
    { label: 'Send SMS message to Arun ("I will be late")', cmd: 'Send a message to Arun saying I will be late', icon: MessageSquare },
    { label: 'Call Contact "Alex"', cmd: 'Call Alex on phone', icon: Phone },
    { label: 'Read Recent Notifications', cmd: 'Read my latest phone notifications', icon: Bell },
  ];

  return (
    <div className={cn('p-5 rounded-3xl bg-slate-950 border border-slate-800 space-y-4 shadow-2xl font-mono text-xs', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2 text-emerald-300 font-extrabold">
          <Smartphone className="w-4 h-4 text-emerald-400" />
          <span className="uppercase tracking-wider">PHONE CONTROL PANEL (PIXEL 8)</span>
        </div>
        <span className="text-[10px] text-emerald-400 font-bold">● CONNECTED</span>
      </div>

      <div className="space-y-2">
        {actions.map((act, idx) => {
          const Icon = act.icon;
          return (
            <div key={idx} className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <Icon className="w-4 h-4 text-emerald-400" />
                <span className="font-sans font-bold text-slate-200 text-xs">{act.label}</span>
              </div>

              <button
                onClick={() => onExecuteCommand(act.cmd)}
                className="px-3 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-[11px] font-bold transition-all cursor-pointer"
              >
                Execute
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PhoneControlPanel;
