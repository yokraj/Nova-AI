import React from 'react';
import { Globe, ShieldAlert, Check, X } from 'lucide-react';
import { cn } from '@/utils/cn';

interface BrowserActionPreviewProps {
  action: string;
  targetUrl: string;
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  requiresApproval: boolean;
  onApprove?: () => void;
  onReject?: () => void;
  className?: string;
}

export const BrowserActionPreview: React.FC<BrowserActionPreviewProps> = ({
  action,
  targetUrl,
  riskLevel,
  requiresApproval,
  onApprove,
  onReject,
  className,
}) => {
  const isHigh = riskLevel === 'HIGH' || riskLevel === 'CRITICAL';

  return (
    <div
      className={cn(
        'p-4 rounded-3xl border space-y-3 font-mono text-xs shadow-2xl',
        isHigh
          ? 'bg-slate-950 border-amber-500/50 text-slate-100'
          : 'bg-slate-950 border-cyan-500/30 text-slate-100',
        className
      )}
    >
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-bold uppercase tracking-wider">
          <Globe className="w-4 h-4 text-cyan-400" />
          <span>BROWSER ACTION: {action}</span>
        </div>
        <span
          className={cn(
            'px-2 py-0.5 rounded-full text-[10px] font-bold border uppercase',
            isHigh ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
          )}
        >
          {riskLevel} RISK
        </span>
      </div>

      <div className="text-[11px] text-slate-300 truncate">
        Target URL: <strong className="text-slate-100">{targetUrl}</strong>
      </div>

      {requiresApproval && (
        <div className="flex items-center justify-between pt-2 border-t border-slate-800">
          <span className="text-[10px] text-amber-300 flex items-center space-x-1">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Form submission or external action requires approval</span>
          </span>
          <div className="flex items-center space-x-2">
            {onReject && (
              <button
                onClick={onReject}
                className="px-3 py-1 rounded-xl bg-slate-900 text-slate-300 hover:text-rose-300 border border-slate-800 font-bold cursor-pointer"
              >
                <X className="w-3.5 h-3.5 inline mr-1" />
                Reject
              </button>
            )}
            {onApprove && (
              <button
                onClick={onApprove}
                className="px-3 py-1 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 font-bold cursor-pointer flex items-center space-x-1"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Approve Action</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BrowserActionPreview;
