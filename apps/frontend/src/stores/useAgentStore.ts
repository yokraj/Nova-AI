import { create } from 'zustand';
import { AgentInfo } from '@/types';
import { MOCK_AGENTS } from '@/mock/mockAgents';

interface AgentState {
  agents: AgentInfo[];
  setAgents: (agents: AgentInfo[]) => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: MOCK_AGENTS,
  setAgents: (agents) => set({ agents }),
}));
