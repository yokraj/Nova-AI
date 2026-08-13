import React from 'react';
import { Globe, CheckCircle2, Loader2, ExternalLink } from 'lucide-react';
import { cn } from '@/utils/cn';

interface BrowserExecutionCardProps {
  action: string;
  targetUrl: string;
  domain?: string;
  targetElement?: string;
  targetingMethod?: string;
  confidence?: number;
  steps: { title: string; status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' }[];
  isSimulated?: boolean;
  className?: string;
}

export const BrowserExecutionCard: React.FC<BrowserExecutionCardProps> = ({
  action,
  targetUrl,
  domain,
  targetElement,
  targetingMethod,
  confidence = 0.96,
  steps,
  isSimulated,
  className,
}) => {
  const confidencePercent = Math.round(confidence * 100);

  return (
    <div className={cn('p-4 rounded-3xl border border-cyan-500/30 bg-slate-950/90 backdrop-blur-xl shadow-2xl space-y-3 font-mono text-xs text-slate-100', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-bold uppercase tracking-wider">
          <Globe className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span>REAL CHROME CDP: {action}</span>
        </div>
        {isSimulated ? (
          <span className="px-2 py-0.5 rounded-full text-[9px] bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold uppercase">
            SIMULATION MODE
          </span>
        ) : (
          <span className="px-2 py-0.5 rounded-full text-[9px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold uppercase">
            CDP VERIFIED
          </span>
        )}
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-300">
        <span className="truncate max-w-[280px] font-bold text-cyan-200">{targetUrl}</span>
        <a href={targetUrl} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300 flex items-center space-x-1">
          <span>{domain || 'web'}</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>

      {targetElement && (
        <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center text-[10px]">
          <span className="text-slate-300">Target: <strong className="text-cyan-200">{targetElement}</strong> ({targetingMethod || 'accessible_name'})</span>
          <span className="text-emerald-400 font-bold">{confidencePercent}%</span>
        </div>
      )}

      <div className="space-y-1.5 pt-1">
        {steps.map((step, idx) => (
          <div key={idx} className="flex items-center space-x-2 text-[11px]">
            {step.status === 'COMPLETED' ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            ) : step.status === 'IN_PROGRESS' ? (
              <Loader2 className="w-3.5 h-3.5 text-amber-400 animate-spin shrink-0" />
            ) : (
              <div className="w-3.5 h-3.5 rounded-full border border-slate-700 shrink-0" />
            )}
            <span className={cn(step.status === 'COMPLETED' ? 'text-slate-200 font-medium' : step.status === 'IN_PROGRESS' ? 'text-amber-300 font-bold' : 'text-slate-500')}>
              {step.title}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BrowserExecutionCard;
