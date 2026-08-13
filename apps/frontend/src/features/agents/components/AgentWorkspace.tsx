import React, { useState } from 'react';
import { Bot, Search, Sparkles } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MOCK_AGENT_WORKFORCE, MOCK_ACTIVE_EXECUTION_TASKS, MOCK_AGENT_TEAMS } from '../mock/mockAgentData';
import { MockAgentEngine } from '../mock/mockAgentEngine';
import { AgentItem } from '../types/agent';
import { AgentExecutionTask } from '../types/agentExecution';
import AgentCard from './AgentCard';
import AgentExecutionCard from './AgentExecutionCard';
import AgentTeamView from './AgentTeamView';
import AgentDetailPanel from './AgentDetailPanel';
import AgentAssignmentDialog from './AgentAssignmentDialog';

export const AgentWorkspace: React.FC = () => {
  const [engine] = useState(new MockAgentEngine());
  const [agents] = useState<AgentItem[]>(MOCK_AGENT_WORKFORCE);
  const [tasks, setTasks] = useState<AgentExecutionTask[]>(MOCK_ACTIVE_EXECUTION_TASKS);
  const [search, setSearch] = useState('');
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [selectedAgent, setSelectedAgent] = useState<AgentItem | null>(null);
  const [isAssignOpen, setIsAssignOpen] = useState(false);

  const domains = ['all', 'Research', 'Software Engineering', 'Security', 'DevOps'];

  const filtered = agents.filter((a) => {
    const matchesSearch =
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.description.toLowerCase().includes(search.toLowerCase()) ||
      a.capabilities.some((c) => c.toLowerCase().includes(search.toLowerCase()));

    const matchesDomain = selectedDomain === 'all' || a.domain === selectedDomain;

    return matchesSearch && matchesDomain;
  });

  const handleStartTask = (agentId: string, title: string) => {
    const newTask = engine.startTask(agentId, title, 'Executing task under Nova OS supervision');
    setTasks((prev) => [newTask, ...prev]);
  };

  const handlePauseTask = (taskId: string) => {
    engine.pauseTask(taskId);
    setTasks([...engine.getTasks()]);
  };

  const handleResumeTask = (taskId: string) => {
    engine.resumeTask(taskId);
    setTasks([...engine.getTasks()]);
  };

  const handleCancelTask = (taskId: string) => {
    engine.cancelTask(taskId);
    setTasks([...engine.getTasks()]);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Stat Panel */}
      <div className="p-6 rounded-3xl bg-slate-900/90 border border-cyan-500/30 flex flex-col md:flex-row items-center justify-between gap-4 shadow-2xl">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Bot className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Nova Agent Workforce</h1>
            <p className="text-xs text-slate-400 font-mono">
              Autonomous multi-agent workforce orchestration • 67 specialized agents across 9 divisions
            </p>
          </div>
        </div>

        {/* Workforce Metrics */}
        <div className="flex items-center space-x-2 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-cyan-400 font-bold">12</span> Active
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-emerald-400 font-bold">8</span> Working
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-slate-400 font-bold">41</span> Idle
          </div>
        </div>
      </div>

      {/* Action & Search Control Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search agents (e.g. 'modify code', 'security')..."
            className="w-full bg-slate-950 border border-slate-800 rounded-2xl py-2 pl-9 pr-4 text-xs text-slate-100 placeholder-slate-500 font-sans focus:outline-none focus:border-cyan-500/50"
          />
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
            {domains.map((dom) => (
              <button
                key={dom}
                onClick={() => setSelectedDomain(dom)}
                className={cn(
                  'px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer capitalize',
                  selectedDomain === dom
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                )}
              >
                {dom}
              </button>
            ))}
          </div>

          <button
            onClick={() => setIsAssignOpen(true)}
            className="px-3 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
          >
            <Sparkles className="w-4 h-4" />
            <span>Assign Task</span>
          </button>
        </div>
      </div>

      {/* Active Executions Stream */}
      {tasks.length > 0 && (
        <div className="space-y-3">
          <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
            Live Agent Task Executions ({tasks.length})
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tasks.map((task) => (
              <AgentExecutionCard
                key={task.id}
                task={task}
                onPause={handlePauseTask}
                onResume={handleResumeTask}
                onCancel={handleCancelTask}
              />
            ))}
          </div>
        </div>
      )}

      {/* Multi-Agent Swarm View */}
      <AgentTeamView team={MOCK_AGENT_TEAMS[0]} />

      {/* Agent Roster Cards Grid */}
      <div className="space-y-3">
        <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
          Specialized Agent Workforce Roster ({filtered.length})
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onSelect={() => setSelectedAgent(agent)}
            />
          ))}
        </div>
      </div>

      {/* Modals & Drawers */}
      <AgentDetailPanel
        agent={selectedAgent}
        onClose={() => setSelectedAgent(null)}
        onStartTask={(agentId) => {
          setSelectedAgent(null);
          setIsAssignOpen(true);
        }}
      />

      <AgentAssignmentDialog
        isOpen={isAssignOpen}
        onClose={() => setIsAssignOpen(false)}
        onConfirmAssignment={(agentId, title) => handleStartTask(agentId, title)}
      />
    </div>
  );
};

export default AgentWorkspace;
