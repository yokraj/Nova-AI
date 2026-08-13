import React from 'react';
import { Eye, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { cn } from '@/utils/cn';

interface VisionAnalysisCardProps {
  action: string;
  activeApp?: string;
  detectedErrors?: string[];
  confidenceScore?: number;
  isSimulated?: boolean;
  className?: string;
}

export const VisionAnalysisCard: React.FC<VisionAnalysisCardProps> = ({
  action,
  activeApp,
  detectedErrors,
  confidenceScore = 0.97,
  isSimulated,
  className,
}) => {
  return (
    <div className={cn('p-4 rounded-3xl border border-cyan-500/30 bg-slate-950/90 backdrop-blur-xl shadow-2xl space-y-3 font-mono text-xs text-slate-100', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-bold uppercase tracking-wider">
          <Eye className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span>VISION ANALYSIS: {action}</span>
        </div>
        {isSimulated && (
          <span className="px-2 py-0.5 rounded-full text-[9px] bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold uppercase">
            SIMULATION MODE
          </span>
        )}
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-300">
        <div>
          Active App: <strong className="text-slate-100">{activeApp || 'VS Code'}</strong>
        </div>
        <div className="flex items-center space-x-1 text-emerald-400">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Confidence: {(confidenceScore * 100).toFixed(0)}%</span>
        </div>
      </div>

      {detectedErrors && detectedErrors.length > 0 && (
        <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-1">
          <div className="flex items-center space-x-1.5 text-amber-300 font-bold text-[11px]">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Detected UI Issues:</span>
          </div>
          {detectedErrors.map((err, idx) => (
            <div key={idx} className="text-[10.5px] text-amber-200/90 pl-5">
              • {err}
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-900">
        <span className="flex items-center space-x-1">
          <CheckCircle2 className="w-3 h-3 text-cyan-400" />
          <span>Privacy Filter: Sensitive data redacted</span>
        </span>
        <span>Ephemeral Inspection</span>
      </div>
    </div>
  );
};

export default VisionAnalysisCard;
