import React from 'react';
import { BarChart3 } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass-panel-cyan p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-cyan-500/10 rounded-xl text-cyan-400 border border-cyan-500/20">
            <BarChart3 className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Enterprise Analytics Engine</h1>
            <p className="text-sm text-slate-400">
              Token usage statistics, latency percentiles, and cost estimations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
