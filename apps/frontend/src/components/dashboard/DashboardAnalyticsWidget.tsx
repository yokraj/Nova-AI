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
import { BarChart3, TrendingUp, Layers, RefreshCw } from 'lucide-react';
import { cn } from '@/utils/cn';
import { AnalyticsSeries } from '@/types/dashboard';
import { MOCK_ANALYTICS_SERIES } from '@/mock/mockDashboardData';
import { useDashboardData } from '@/hooks/useDashboardData';

export interface DashboardAnalyticsWidgetProps {
  className?: string;
  data?: AnalyticsSeries;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export const DashboardAnalyticsWidget: React.FC<DashboardAnalyticsWidgetProps> = ({
  className,
  data: externalData,
  onRefresh,
  isLoading: externalIsLoading,
}) => {
  const [activeTab, setActiveTab] = useState<'requests' | 'agents' | 'memory'>('requests');
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d'>('24h');

  // Hook into live dashboard data
  const {
    data: dashboardData,
    connectionStatus,
    isRefreshing,
    refresh: hookRefresh,
  } = useDashboardData();

  const isConnected = connectionStatus === 'connected' && !!dashboardData?.isConnected;
  const data = externalData || (isConnected ? dashboardData?.analytics : undefined) || MOCK_ANALYTICS_SERIES;
  const lastUpdated = dashboardData?.lastUpdated;
  const isLoading = externalIsLoading !== undefined ? externalIsLoading : isRefreshing;

  const handleRefreshClick = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      hookRefresh(true);
    }
  };

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/80 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
                Telemetry Analytics & AI Workload
              </h3>
              {lastUpdated && (
                <span className="text-[10px] font-mono text-slate-500 hidden sm:inline">
                  • Polled: {new Date(lastUpdated).toLocaleTimeString()}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Request throughput, agent task density & memory growth
            </p>
          </div>
        </div>

        {/* Tab & Timeframe Buttons + Refresh */}
        <div className="flex items-center space-x-2 flex-wrap gap-1">
          <button
            onClick={handleRefreshClick}
            disabled={isLoading}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer disabled:opacity-50"
            title="Refresh Analytics"
            aria-label="Refresh analytics"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', isLoading && 'animate-spin text-cyan-400')} />
          </button>

          {isConnected ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>HISTORICAL METRICS (LIVE)</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 text-slate-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full border border-slate-400" />
              <span>STANDALONE SNAPSHOT</span>
            </span>
          )}

          {/* Metric Tabs */}
          <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-xs font-mono">
            <button
              onClick={() => setActiveTab('requests')}
              className={cn(
                'px-2.5 py-1 rounded-lg flex items-center space-x-1.5 transition-all cursor-pointer',
                activeTab === 'requests'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Requests</span>
            </button>
            <button
              onClick={() => setActiveTab('agents')}
              className={cn(
                'px-2.5 py-1 rounded-lg flex items-center space-x-1.5 transition-all cursor-pointer',
                activeTab === 'agents'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Agents</span>
            </button>
            <button
              onClick={() => setActiveTab('memory')}
              className={cn(
                'px-2.5 py-1 rounded-lg flex items-center space-x-1.5 transition-all cursor-pointer',
                activeTab === 'memory'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Memory</span>
            </button>
          </div>

          {/* Timeframe Pill */}
          <div className="hidden sm:flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono">
            {(['24h', '7d', '30d'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={cn(
                  'px-2 py-0.5 rounded-lg transition-all cursor-pointer',
                  timeframe === tf
                    ? 'bg-slate-800 text-slate-100 font-bold'
                    : 'text-slate-500 hover:text-slate-300'
                )}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Canvas Area */}
      <div className="h-64 w-full pt-2">
        {activeTab === 'requests' && (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.aiRequestsOverTime}>
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
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#00f0ff',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                }}
              />
              <Area
                type="monotone"
                dataKey="requests"
                stroke="#00f0ff"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#requestsGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {activeTab === 'agents' && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.agentActivityDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#a855f7',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                }}
              />
              <Bar dataKey="tasks" fill="#a855f7" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}

        {activeTab === 'memory' && (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.memoryGrowth}>
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
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#10b981',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                }}
              />
              <Area
                type="monotone"
                dataKey="memories"
                stroke="#10b981"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#memoryGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Footer Metrics */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs font-mono text-slate-400 pt-2 border-t border-slate-800/80 gap-2">
        <span>
          Peak Throughput: <strong className="text-cyan-300">1,560 req/min</strong>
        </span>
        <span>
          Average Latency: <strong className="text-emerald-400">12.4 ms</strong>
        </span>
        <span>
          Window: <strong className="text-purple-300">{timeframe.toUpperCase()} Rolling</strong>
        </span>
      </div>
    </div>
  );
};

export default DashboardAnalyticsWidget;
