import React, { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  CartesianGrid,
} from 'recharts';
import { BarChart3, TrendingUp, Layers } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_ANALYTICS_SERIES } from '@/mock/mockDashboardData';

export const DashboardAnalyticsWidget: React.FC<{ className?: string }> = ({ className }) => {
  const [activeTab, setActiveTab] = useState<'requests' | 'agents' | 'memory'>('requests');

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Telemetry Analytics & AI Workload
            </h3>
            <p className="text-xs text-slate-400">Request throughput, agent task density & memory growth</p>
          </div>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('requests')}
            className={cn(
              'px-3 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
              activeTab === 'requests' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            <span>AI Requests</span>
          </button>
          <button
            onClick={() => setActiveTab('agents')}
            className={cn(
              'px-3 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
              activeTab === 'agents' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Agent Tasks</span>
          </button>
          <button
            onClick={() => setActiveTab('memory')}
            className={cn(
              'px-3 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
              activeTab === 'memory' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Memory Growth</span>
          </button>
        </div>
      </div>

      {/* Chart Canvas Area */}
      <div className="h-64 w-full pt-2">
        {activeTab === 'requests' && (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={MOCK_ANALYTICS_SERIES.aiRequestsOverTime}>
              <defs>
                <linearGradient id="requestsGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#00f0ff" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <RechartsTooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#00f0ff', borderRadius: '12px', fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="requests" stroke="#00f0ff" strokeWidth={2} fillOpacity={1} fill="url(#requestsGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {activeTab === 'agents' && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={MOCK_ANALYTICS_SERIES.agentActivityDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <RechartsTooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#a855f7', borderRadius: '12px', fontSize: '12px' }}
              />
              <Bar dataKey="tasks" fill="#a855f7" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}

        {activeTab === 'memory' && (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={MOCK_ANALYTICS_SERIES.memoryGrowth}>
              <defs>
                <linearGradient id="memoryGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <RechartsTooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#10b981', borderRadius: '12px', fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="memories" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#memoryGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-2 border-t border-slate-800">
        <span>Peak Throughput: <strong className="text-cyan-300">1,560 req/min</strong></span>
        <span>Average Latency: <strong className="text-emerald-400">12.4 ms</strong></span>
      </div>
    </GlassCard>
  );
};

export default DashboardAnalyticsWidget;
