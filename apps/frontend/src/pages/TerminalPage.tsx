import React from 'react';
import { Terminal } from 'lucide-react';

export const TerminalPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass-panel-cyan p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-cyan-500/10 rounded-xl text-cyan-400 border border-cyan-500/20">
            <Terminal className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Interactive CLI Terminal</h1>
            <p className="text-sm text-slate-400">
              Desktop automation, script execution console, and system logs
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TerminalPage;
