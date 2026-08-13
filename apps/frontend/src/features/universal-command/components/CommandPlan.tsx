import React from 'react';
import { CheckCircle2, Clock } from 'lucide-react';
import { cn } from '@/utils/cn';
import { CommandPlan as PlanType } from '../types/execution';

interface CommandPlanProps {
  plan: PlanType;
  className?: string;
}

export const CommandPlanView: React.FC<CommandPlanProps> = ({ plan, className }) => {
  return (
    <div className={cn('p-4 rounded-3xl bg-slate-950 border border-slate-800 space-y-3 font-mono text-xs shadow-xl', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2 text-slate-400 font-bold uppercase tracking-wider">
        <span>EXECUTION PLAN</span>
        <span className="text-[10px] text-slate-500">{plan.steps.length} Steps</span>
      </div>

      <div className="space-y-2">
        {plan.steps.map((step) => (
          <div key={step.id} className="p-2.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="w-5 h-5 rounded-full bg-slate-800 text-cyan-300 font-bold flex items-center justify-center text-[10px]">
                {step.stepNumber}
              </span>
              <div>
                <div className="font-sans font-bold text-slate-200 text-xs">{step.title}</div>
                <div className="text-[10px] text-slate-500">{step.description}</div>
              </div>
            </div>

            {step.status === 'COMPLETED' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ) : (
              <Clock className="w-4 h-4 text-slate-600 animate-pulse" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CommandPlanView;
