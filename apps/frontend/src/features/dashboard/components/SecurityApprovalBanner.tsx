import React, { useState } from 'react';
import { ShieldAlert, Check, X, ShieldCheck } from 'lucide-react';
import { cn } from '@/utils/cn';
import { SecurityApprovalRequest } from '../types';

export const MOCK_SECURITY_REQUESTS: SecurityApprovalRequest[] = [
  {
    id: 'sec-01',
    title: 'Deploy FastAPI Containerized Topology to Local Docker Host',
    requesterAgent: 'DevOps & Release Manager Agent',
    actionType: 'Admin Action',
    riskLevel: 'medium',
    timestamp: '2 mins ago',
  },
  {
    id: 'sec-02',
    title: 'Modify Registry Environment Variables for Production Build',
    requesterAgent: 'Security Engineer Agent',
    actionType: 'Sensitive Action',
    riskLevel: 'high',
    timestamp: '5 mins ago',
  },
];

export const SecurityApprovalBanner: React.FC<{ className?: string }> = ({ className }) => {
  const [requests, setRequests] = useState<SecurityApprovalRequest[]>(MOCK_SECURITY_REQUESTS);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const handleAction = (id: string, approved: boolean, title: string) => {
    setRequests((prev) => prev.filter((r) => r.id !== id));
    setActionFeedback(
      approved
        ? `[Security Gate] Action Approved: '${title}'`
        : `[Security Gate] Action Rejected & Blocked: '${title}'`
    );
  };

  if (requests.length === 0 && !actionFeedback) {
    return null;
  }

  return (
    <div className={cn('p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-xs font-mono space-y-3', className)}>
      <div className="flex items-center justify-between border-b border-amber-500/20 pb-2">
        <div className="flex items-center space-x-2 text-amber-300 font-bold">
          <ShieldAlert className="w-4 h-4 text-amber-400 animate-pulse" />
          <span>Security UX • Agent Action Approval Required</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
          {requests.length} PENDING APPROVALS
        </span>
      </div>

      {actionFeedback ? (
        <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-cyan-300 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>{actionFeedback}</span>
          </div>
          <button onClick={() => setActionFeedback(null)} className="text-slate-400 hover:text-slate-200">
            Dismiss
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {requests.map((req) => (
            <div
              key={req.id}
              className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded-full text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">
                    {req.actionType}
                  </span>
                  <span className="font-bold text-slate-100">{req.title}</span>
                </div>
                <div className="text-[11px] text-slate-400 flex items-center space-x-2">
                  <span>Requested by: <strong className="text-cyan-300">{req.requesterAgent}</strong></span>
                  <span>•</span>
                  <span>Risk: <strong className="text-amber-400 uppercase">{req.riskLevel}</strong></span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleAction(req.id, true, req.title)}
                  className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 font-bold flex items-center space-x-1 transition-all cursor-pointer"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Approve</span>
                </button>
                <button
                  onClick={() => handleAction(req.id, false, req.title)}
                  className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 font-bold flex items-center space-x-1 transition-all cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SecurityApprovalBanner;
