import { AgentItem, AgentProvider } from '../types/agent';
import { AgentExecutionTask, AgentExecutionProvider } from '../types/agentExecution';
import { MOCK_AGENT_WORKFORCE, MOCK_ACTIVE_EXECUTION_TASKS } from './mockAgentData';

export class MockAgentEngine implements AgentProvider, AgentExecutionProvider {
  private agents: AgentItem[] = [...MOCK_AGENT_WORKFORCE];
  private tasks: AgentExecutionTask[] = [...MOCK_ACTIVE_EXECUTION_TASKS];

  listAgents(): AgentItem[] {
    return this.agents;
  }

  getAgentById(id: string): AgentItem | undefined {
    return this.agents.find((a) => a.id === id);
  }

  searchAgents(query: string, domain?: string): AgentItem[] {
    return this.agents.filter((a) => {
      const matchesQuery =
        a.name.toLowerCase().includes(query.toLowerCase()) ||
        a.description.toLowerCase().includes(query.toLowerCase()) ||
        a.capabilities.some((c) => c.toLowerCase().includes(query.toLowerCase()));

      const matchesDomain = !domain || domain === 'all' || a.domain === domain;

      return matchesQuery && matchesDomain;
    });
  }

  startTask(agentId: string, title: string, description: string): AgentExecutionTask {
    const agent = this.getAgentById(agentId);
    const newTask: AgentExecutionTask = {
      id: `tsk-${Date.now()}`,
      agentId,
      agentName: agent ? agent.name : 'Specialized Agent',
      title,
      description,
      status: 'WORKING',
      progress: 10,
      currentAction: `Executing task "${title}"...`,
      toolsUsed: agent ? agent.tools.slice(0, 2) : ['Memory Store'],
      outputLogs: [`Initiated task "${title}" under Nova AI Operating System orchestration.`],
      startedAt: new Date().toLocaleTimeString(),
    };

    this.tasks.unshift(newTask);
    return newTask;
  }

  pauseTask(taskId: string) {
    const task = this.tasks.find((t) => t.id === taskId);
    if (task) task.status = 'PAUSED';
  }

  resumeTask(taskId: string) {
    const task = this.tasks.find((t) => t.id === taskId);
    if (task) task.status = 'WORKING';
  }

  cancelTask(taskId: string) {
    const task = this.tasks.find((t) => t.id === taskId);
    if (task) task.status = 'CANCELLED';
  }

  retryTask(taskId: string) {
    const task = this.tasks.find((t) => t.id === taskId);
    if (task) {
      task.status = 'WORKING';
      task.progress = 20;
    }
  }

  getTasks(): AgentExecutionTask[] {
    return this.tasks;
  }
}
