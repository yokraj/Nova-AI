import React from 'react';
import { Settings } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass-panel-cyan p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-cyan-500/10 rounded-xl text-cyan-400 border border-cyan-500/20">
            <Settings className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">System Preferences & Security</h1>
            <p className="text-sm text-slate-400">
              RBAC permissions, workspace configurations, and theme customization
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
