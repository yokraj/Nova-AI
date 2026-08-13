import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ShieldAlert, ArrowRight, Bot } from 'lucide-react';
import { cn } from '@/utils/cn';
import { NovaResponse as NovaResponseType } from '../types/novaCommand';
import { NovaContextDrawerType } from '../types/novaCore';

interface NovaResponseProps {
  response: NovaResponseType;
  onApproveSecurity?: () => void;
  onRejectSecurity?: () => void;
  onOpenContextDrawer?: (drawer: NovaContextDrawerType) => void;
  className?: string;
}

export const NovaResponse: React.FC<NovaResponseProps> = ({
  response,
  onApproveSecurity,
  onRejectSecurity,
  onOpenContextDrawer,
  className,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      className={cn('w-full max-w-3xl mx-auto p-5 rounded-3xl bg-slate-900/90 border border-cyan-500/40 text-slate-100 shadow-[0_0_30px_rgba(0,240,255,0.12)] space-y-4 font-sans', className)}
    >
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span className="text-xs font-mono font-bold text-cyan-300 uppercase">NOVA RESPONSE</span>
        </div>
        {response.missionId && (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">
            MISSION: {response.missionId}
          </span>
        )}
      </div>

      {/* Main Spoken Response Text */}
      <div className="text-sm font-medium text-slate-200 leading-relaxed font-sans">
        "{response.spokenText}"
      </div>

      {/* Detailed Payload Output */}
      {response.detailedOutput && (
        <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800/80 text-xs font-mono text-slate-400">
          {response.detailedOutput}
        </div>
      )}

      {/* Security Approval Gate (If required) */}
      {response.securityApprovalRequired && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-xs font-mono space-y-3">
          <div className="flex items-center space-x-2 text-amber-300 font-bold">
            <ShieldAlert className="w-4 h-4 text-amber-400 animate-pulse" />
            <span>APPROVAL REQUIRED • {response.securityRiskLevel || 'MEDIUM'} RISK</span>
          </div>
          <p className="text-slate-300 font-sans">{response.securityActionTitle}</p>
          <div className="flex items-center space-x-2 pt-1">
            <button
              onClick={onApproveSecurity}
              className="px-3.5 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-bold font-mono transition-all cursor-pointer"
            >
              APPROVE ACTION
            </button>
            <button
              onClick={onRejectSecurity}
              className="px-3.5 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-xs font-bold font-mono transition-all cursor-pointer"
            >
              REJECT
            </button>
          </div>
        </div>
      )}

      {/* Contextual Workspace Trigger Chips */}
      <div className="flex items-center justify-between pt-1 text-xs font-mono">
        {response.assignedAgent ? (
          <div className="flex items-center space-x-1.5 text-cyan-400">
            <Bot className="w-3.5 h-3.5" />
            <span>Assigned Agent: <strong className="text-slate-100">{response.assignedAgent}</strong></span>
          </div>
        ) : <div />}

        {response.suggestedDrawer && (
          <button
            onClick={() => onOpenContextDrawer?.(response.suggestedDrawer as NovaContextDrawerType)}
            className="text-cyan-400 hover:text-cyan-200 flex items-center space-x-1 font-bold cursor-pointer"
          >
            <span>View {response.suggestedDrawer.toUpperCase()} Context</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default NovaResponse;
