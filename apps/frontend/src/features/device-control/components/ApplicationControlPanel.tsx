import React from 'react';
import { AppWindow, Play } from 'lucide-react';
import { cn } from '@/utils/cn';

interface ApplicationControlPanelProps {
  onExecuteCommand: (cmd: string) => void;
  className?: string;
}

export const ApplicationControlPanel: React.FC<ApplicationControlPanelProps> = ({
  onExecuteCommand,
  className,
}) => {
  const apps = [
    { name: 'Visual Studio Code', icon: '💻', status: 'Installed', cmd: 'Open Visual Studio Code' },
    { name: 'Google Chrome', icon: '🌐', status: 'Installed', cmd: 'Open Google Chrome' },
    { name: 'Windows Terminal', icon: '⚡', status: 'Installed', cmd: 'Open Terminal' },
    { name: 'Spotify Music', icon: '🎵', status: 'Installed', cmd: 'Open Spotify' },
  ];

  return (
    <div className={cn('p-5 rounded-3xl bg-slate-950 border border-slate-800 space-y-4 shadow-2xl font-mono text-xs', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
          <AppWindow className="w-4 h-4 text-cyan-400" />
          <span className="uppercase tracking-wider">APPLICATION CONTROL PANEL</span>
        </div>
        <span className="text-[10px] text-slate-500">4 Applications Detected</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {apps.map((app) => (
          <div key={app.name} className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="text-xl">{app.icon}</span>
              <div>
                <div className="font-sans font-bold text-slate-100 text-xs">{app.name}</div>
                <div className="text-[10px] text-emerald-400 font-bold">{app.status}</div>
              </div>
            </div>

            <button
              onClick={() => onExecuteCommand(app.cmd)}
              className="px-3 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-[11px] font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Play className="w-3 h-3" />
              <span>Launch</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ApplicationControlPanel;
