export interface AgentTeamMember {
  agentId: string;
  role: string;
  dependencies: string[]; // Dependee agent IDs
}

export interface AgentTeam {
  id: string;
  name: string;
  description: string;
  missionId: string;
  leadAgentId: string;
  members: AgentTeamMember[];
  status: 'planning' | 'executing' | 'completed' | 'failed';
}
