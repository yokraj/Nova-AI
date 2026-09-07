import React from 'react';
import { BackgroundRuntimeDrawer } from '@/features/background-runtime/components/BackgroundRuntimeDrawer';

export const AutomationPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h1 className="text-xl font-extrabold text-slate-100 font-sans tracking-wide">Background Automation Runtime</h1>
          <p className="text-xs text-slate-400 font-mono">Persistent local task scheduler, recurring background jobs, event triggers, and execution history.</p>
        </div>
      </div>
      <BackgroundRuntimeDrawer />
    </div>
  );
};

export default AutomationPage;
