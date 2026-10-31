import React, { useState } from 'react';
import { Server, CheckCircle2, AlertTriangle, XCircle, RefreshCw, Filter } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ServiceHealthItem } from '@/types/dashboard';

const DEFAULT_CORE_SERVICES: ServiceHealthItem[] = [
  { id: 'srv-1', name: 'Universal Intelligence', category: 'Core Engine', status: 'healthy', latencyMs: 12, healthMetric: '100% Operational', port: 8000 },
  { id: 'srv-2', name: 'Memory Platform', category: 'Memory', status: 'healthy', latencyMs: 4, healthMetric: '142.8k Vectors', port: 6333 },
  { id: 'srv-3', name: 'Vector Memory', category: 'Storage', status: 'healthy', latencyMs: 6, healthMetric: 'HNSW Index Active', port: 6334 },
  { id: 'srv-4', name: 'Hybrid RAG', category: 'Search', status: 'healthy', latencyMs: 15, healthMetric: 'Grounded Context', port: 8001 },
  { id: 'srv-5', name: 'Knowledge Graph', category: 'Graph', status: 'healthy', latencyMs: 8, healthMetric: '12.5k Entities', port: 7687 },
  { id: 'srv-6', name: 'Context Engine', category: 'Context', status: 'healthy', latencyMs: 3, healthMetric: 'Active Tracking', port: 8002 },
  { id: 'srv-7', name: 'Inference Gateway', category: 'AI Models', status: 'healthy', latencyMs: 14, healthMetric: 'Ollama qwen3:8b', port: 11434 },
  { id: 'srv-8', name: 'Code Intelligence', category: 'Engineering', status: 'healthy', latencyMs: 18, healthMetric: 'AST Parser Ready', port: 8003 },
];

interface NovaCoreServicesWidgetProps {
  className?: string;
  services?: ServiceHealthItem[];
  onRestartService?: (id: string) => void;
}

export const NovaCoreServicesWidget: React.FC<NovaCoreServicesWidgetProps> = ({
  className,
  services = DEFAULT_CORE_SERVICES,
  onRestartService,
}) => {
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [restartingId, setRestartingId] = useState<string | null>(null);

  const categories = ['all', 'Core Engine', 'Memory', 'Storage', 'Search', 'Graph', 'AI Models', 'Engineering'];

  const filteredServices = services.filter((s) => {
    if (activeCategory === 'all') return true;
    return s.category.toLowerCase() === activeCategory.toLowerCase();
  });

  const handleRestart = (id: string) => {
    setRestartingId(id);
    setTimeout(() => {
      setRestartingId(null);
      if (onRestartService) onRestartService(id);
    }, 1200);
  };

  const healthyCount = services.filter((s) => s.status === 'healthy').length;
  const isAllHealthy = healthyCount === services.length && services.length > 0;
  const isPartiallyHealthy = healthyCount > 0 && !isAllHealthy;

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              Nova Core Services Health
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              {healthyCount}/{services.length} AI OS microservices online
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center space-x-2">
          {isAllHealthy ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>{healthyCount}/{services.length} HEALTHY</span>
            </span>
          ) : isPartiallyHealthy ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>{healthyCount}/{services.length} DEGRADED</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
              <span>DISCONNECTED</span>
            </span>
          )}
        </div>
      </div>

      {/* Category Filter Tabs */}
      <div className="flex items-center space-x-1 overflow-x-auto pb-1 scrollbar-none text-[11px] font-mono">
        <Filter className="w-3.5 h-3.5 text-slate-500 mr-1 shrink-0" />
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={cn(
              'px-2.5 py-1 rounded-lg transition-all cursor-pointer whitespace-nowrap',
              activeCategory === cat
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
            )}
          >
            {cat === 'all' ? 'All Services' : cat}
          </button>
        ))}
      </div>

      {/* Grid of Core Services */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {filteredServices.map((srv) => (
          <div
            key={srv.id}
            className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all space-y-2.5 group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5 min-w-0">
                {srv.status === 'healthy' ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                ) : srv.status === 'degraded' ? (
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                ) : (
                  <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                )}
                <h4 className="text-xs font-bold text-slate-100 truncate">{srv.name}</h4>
              </div>
              <span className="text-[10px] font-mono text-cyan-400 font-bold shrink-0">{srv.latencyMs}ms</span>
            </div>

            <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
              <span className="bg-slate-800/90 px-2 py-0.5 rounded-full text-slate-300">{srv.category}</span>
              <span
                className={cn(
                  'font-semibold truncate',
                  srv.status === 'healthy'
                    ? 'text-emerald-400'
                    : srv.status === 'degraded'
                    ? 'text-amber-400'
                    : 'text-rose-400'
                )}
              >
                {srv.healthMetric}
              </span>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-slate-800/60 text-[10px] font-mono text-slate-500">
              <span>Port: {srv.port || 8000}</span>
              <button
                onClick={() => handleRestart(srv.id)}
                disabled={restartingId === srv.id}
                className="text-slate-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer disabled:opacity-50"
                title="Restart service"
              >
                <RefreshCw className={cn('w-2.5 h-2.5', restartingId === srv.id && 'animate-spin text-cyan-400')} />
                <span>{restartingId === srv.id ? 'Cycling...' : 'Restart'}</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NovaCoreServicesWidget;
