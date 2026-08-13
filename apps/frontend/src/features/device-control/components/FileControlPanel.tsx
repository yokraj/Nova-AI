import React from 'react';
import { Folder, Search, Plus, ArrowRight } from 'lucide-react';
import { cn } from '@/utils/cn';

interface FileControlPanelProps {
  onExecuteCommand: (cmd: string) => void;
  className?: string;
}

export const FileControlPanel: React.FC<FileControlPanelProps> = ({
  onExecuteCommand,
  className,
}) => {
  const actions = [
    { label: 'Find all PDF files in Downloads', cmd: 'Find my PDF files in Downloads', icon: Search },
    { label: 'Create folder "Projects"', cmd: 'Create a folder called Projects', icon: Plus },
    { label: 'Move files into Documents', cmd: 'Move recent PDF files into Documents', icon: ArrowRight },
  ];

  return (
    <div className={cn('p-5 rounded-3xl bg-slate-950 border border-slate-800 space-y-4 shadow-2xl font-mono text-xs', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2 text-purple-300 font-extrabold">
          <Folder className="w-4 h-4 text-purple-400" />
          <span className="uppercase tracking-wider">FILE SYSTEM CONTROL PANEL</span>
        </div>
        <span className="text-[10px] text-slate-500">Local FS Scope</span>
      </div>

      <div className="space-y-2">
        {actions.map((act, idx) => {
          const Icon = act.icon;
          return (
            <div key={idx} className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <Icon className="w-4 h-4 text-purple-400" />
                <span className="font-sans font-bold text-slate-200 text-xs">{act.label}</span>
              </div>

              <button
                onClick={() => onExecuteCommand(act.cmd)}
                className="px-3 py-1.5 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 text-[11px] font-bold transition-all cursor-pointer"
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

export default FileControlPanel;
