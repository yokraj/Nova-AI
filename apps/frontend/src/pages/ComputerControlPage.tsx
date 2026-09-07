import React from 'react';
import DeviceControlWorkspace from '@/features/device-control/components/DeviceControlWorkspace';

export const ComputerControlPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h1 className="text-xl font-extrabold text-slate-100 font-sans tracking-wide">Computer & Device Control</h1>
          <p className="text-xs text-slate-400 font-mono">Real-time desktop interaction, window handles, display target grounding, and native bridge control.</p>
        </div>
      </div>
      <DeviceControlWorkspace />
    </div>
  );
};

export default ComputerControlPage;
