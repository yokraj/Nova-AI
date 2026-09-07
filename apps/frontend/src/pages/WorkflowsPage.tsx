import React from 'react';
import { WorkflowStudioCanvas } from '@/features/workflow-studio/components/WorkflowStudioCanvas';

export const WorkflowsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h1 className="text-xl font-extrabold text-slate-100 font-sans tracking-wide">Production Workflow Studio</h1>
          <p className="text-xs text-slate-400 font-mono">Interactive DAG builder, dry-run test mode, target relocator, and multi-agent swarm replay engine.</p>
        </div>
      </div>
      <WorkflowStudioCanvas />
    </div>
  );
};

export default WorkflowsPage;
