import React from 'react';
import { Server, CheckCircle2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { StatusBadge } from '@/components/status/StatusIndicators';

export interface ServiceHealthItem {
  id: string;
  name: string;
  category: string;
  status: 'healthy' | 'degraded' | 'maintenance';
  latencyMs: number;
  healthMetric: string;
}

export const MOCK_CORE_SERVICES: ServiceHealthItem[] = [
  { id: 'srv-1', name: 'Universal Intelligence', category: 'Core Engine', status: 'healthy', latencyMs: 12, healthMetric: '100% Operational' },
  { id: 'srv-2', name: 'Memory Platform', category: 'Memory', status: 'healthy', latencyMs: 4, healthMetric: '142.8k Vectors' },
  { id: 'srv-3', name: 'Vector Memory', category: 'Storage', status: 'healthy', latencyMs: 6, healthMetric: 'HNSW Index Active' },
  { id: 'srv-4', name: 'Hybrid RAG', category: 'Search', status: 'healthy', latencyMs: 15, healthMetric: 'Grounded Context' },
  { id: 'srv-5', name: 'Knowledge Graph', category: 'Graph', status: 'healthy', latencyMs: 8, healthMetric: '12.5k Entities' },
  { id: 'srv-6', name: 'Context Engine', category: 'Context', status: 'healthy', latencyMs: 3, healthMetric: 'Active Tracking' },
  { id: 'srv-7', name: 'Inference Gateway', category: 'AI Models', status: 'healthy', latencyMs: 14, healthMetric: 'Ollama qwen3:8b' },
  { id: 'srv-8', name: 'Code Intelligence', category: 'Engineering', status: 'healthy', latencyMs: 18, healthMetric: 'AST Parser Ready' },
];

export const NovaCoreServicesWidget: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Nova Core Services Health
            </h3>
            <p className="text-xs text-slate-400">8 Critical AI OS services operating nominal</p>
          </div>
        </div>
        <StatusBadge label="8/8 HEALTHY" variant="success" />
      </div>

      {/* Grid of 8 Core Services */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {MOCK_CORE_SERVICES.map((srv) => (
          <div
            key={srv.id}
            className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <h4 className="text-xs font-bold text-slate-100 truncate">{srv.name}</h4>
              </div>
              <span className="text-[10px] font-mono text-cyan-400 font-bold">{srv.latencyMs}ms</span>
            </div>

            <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
              <span className="bg-slate-800/90 px-2 py-0.5 rounded-full text-slate-300">{srv.category}</span>
              <span className="text-emerald-400 font-semibold">{srv.healthMetric}</span>
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
};

export default NovaCoreServicesWidget;
