import React from 'react';
import { Network, Bot } from 'lucide-react';
import { cn } from '@/utils/cn';
import { AgentTeam } from '../types/agentTeam';
import { MOCK_AGENT_WORKFORCE } from '../mock/mockAgentData';

interface AgentTeamViewProps {
  team: AgentTeam;
  className?: string;
}

export const AgentTeamView: React.FC<AgentTeamViewProps> = ({ team, className }) => {
  return (
    <div className={cn('p-5 rounded-3xl bg-slate-950 border border-purple-500/30 space-y-4 shadow-2xl font-mono text-xs', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2 text-purple-300 font-extrabold">
          <Network className="w-4 h-4 text-purple-400 animate-pulse" />
          <span className="uppercase tracking-wider">MULTI-AGENT TEAM SWARM ({team.name})</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 uppercase font-bold text-[10px]">
          {team.status}
        </span>
      </div>

      {/* Conceptual Hierarchy Flow */}
      <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4 text-center">
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-bold">
          <Bot className="w-4 h-4 text-cyan-400" />
          <span>NOVA AI OPERATING SYSTEM ORCHESTRATOR</span>
        </div>

        <div className="flex justify-center">
          <div className="w-0.5 h-6 bg-slate-700" />
        </div>

        {/* Member Swarm Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {team.members.map((m) => {
            const memberAgent = MOCK_AGENT_WORKFORCE.find((a) => a.id === m.agentId);
            return (
              <div key={m.agentId} className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-left space-y-1 shadow-md">
                <div className="text-[10px] text-purple-400 font-bold uppercase">{m.role}</div>
                <div className="text-xs font-bold text-slate-100 font-sans">{memberAgent?.name || m.agentId}</div>
                <div className="text-[10px] text-slate-400">Status: {memberAgent?.status || 'Active'}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AgentTeamView;
