import { SwarmTask, SwarmAgent, SwarmDependency } from '../types/swarm';

export class SwarmTaskDecomposer {
  decomposeGoal(goal: string, agents: SwarmAgent[]): { tasks: SwarmTask[]; dependencies: SwarmDependency[] } {
    const lowerGoal = goal.toLowerCase();
    const tasks: SwarmTask[] = [];
    const dependencies: SwarmDependency[] = [];

    const getAgent = (domainKeyword: string) =>
      agents.find((a) => a.domain.toLowerCase().includes(domainKeyword) || a.capabilities.some((c) => c.toLowerCase().includes(domainKeyword))) || agents[0];

    const archAgent = getAgent('planning');
    const opsAgent = getAgent('system operations');
    const secAgent = getAgent('security');
    const qaAgent = getAgent('testing');
    const visAgent = getAgent('analysis');

    // Task 1: Architecture & System Analysis (Independent / Parallel)
    const t1Id = `task-1-${Date.now()}`;
    tasks.push({
      taskId: t1Id,
      title: 'Analyze Goal & Environment',
      description: 'Analyze system environment and target file paths',
      assignedAgentId: archAgent.agentId,
      assignedAgentName: archAgent.name,
      state: 'PARALLEL',
      priority: 'HIGH',
      toolName: 'system.get_info',
      toolArguments: {},
      dependencies: [],
    });

    if (lowerGoal.includes('screen') || lowerGoal.includes('screenshot')) {
      const tVisId = `task-vis-${Date.now()}`;
      tasks.push({
        taskId: tVisId,
        title: 'Capture Visual Screen State',
        description: 'Capture active screen display frame',
        assignedAgentId: visAgent.agentId,
        assignedAgentName: visAgent.name,
        state: 'PARALLEL',
        priority: 'NORMAL',
        toolName: 'system.screenshot_capture',
        toolArguments: {},
        dependencies: [],
      });
    }

    if (lowerGoal.includes('create') || lowerGoal.includes('folder') || lowerGoal.includes('project') || lowerGoal.includes('deploy') || lowerGoal.includes('readme')) {
      // Task 2: Provision Root Directory (Depends on T1)
      const t2Id = `task-2-${Date.now()}`;
      tasks.push({
        taskId: t2Id,
        title: 'Provision Directory Workspace',
        description: 'Create root project directory on local disk',
        assignedAgentId: opsAgent.agentId,
        assignedAgentName: opsAgent.name,
        state: 'DEPENDENCY_BLOCKED',
        priority: 'NORMAL',
        toolName: 'filesystem.create_directory',
        toolArguments: { path: 'c:\\Projects\\Nova-AI\\apps\\frontend\\.nova_swarm_workspace' },
        dependencies: [t1Id],
      });
      dependencies.push({ taskId: t2Id, dependsOnTaskId: t1Id });

      // Task 3: Provision File & Write Content (Depends on T2)
      const t3Id = `task-3-${Date.now()}`;
      tasks.push({
        taskId: t3Id,
        title: 'Write Documentation Payload',
        description: 'Write README file content to project directory',
        assignedAgentId: opsAgent.agentId,
        assignedAgentName: opsAgent.name,
        state: 'DEPENDENCY_BLOCKED',
        priority: 'NORMAL',
        toolName: 'filesystem.write_file',
        toolArguments: {
          path: 'c:\\Projects\\Nova-AI\\apps\\frontend\\.nova_swarm_workspace\\README.txt',
          content: 'Nova AI Multi-Agent Swarm Workspace Initialized Successfully.',
        },
        dependencies: [t2Id],
      });
      dependencies.push({ taskId: t3Id, dependsOnTaskId: t2Id });
    }

    if (lowerGoal.includes('security') || lowerGoal.includes('permission') || lowerGoal.includes('scan') || lowerGoal.includes('deploy')) {
      const tSecId = `task-sec-${Date.now()}`;
      tasks.push({
        taskId: tSecId,
        title: 'Run Security & Policy Audit',
        description: 'Audit file permissions and active system security posture',
        assignedAgentId: secAgent.agentId,
        assignedAgentName: secAgent.name,
        state: 'PARALLEL',
        priority: 'HIGH',
        toolName: 'system.process_list',
        toolArguments: {},
        dependencies: [],
      });
    }

    // Final Task: QA Verification (Depends on preceding tasks)
    const tQaId = `task-qa-${Date.now()}`;
    const upstreamIds = tasks.filter((t) => t.taskId !== tQaId).map((t) => t.taskId);
    tasks.push({
      taskId: tQaId,
      title: 'Verify Swarm Output Integrity',
      description: 'Audit created files and verify final task outputs',
      assignedAgentId: qaAgent.agentId,
      assignedAgentName: qaAgent.name,
      state: 'DEPENDENCY_BLOCKED',
      priority: 'HIGH',
      toolName: 'filesystem.read_file',
      toolArguments: { path: 'c:\\Projects\\Nova-AI\\apps\\frontend\\.nova_swarm_workspace\\README.txt' },
      dependencies: upstreamIds,
    });

    for (const upId of upstreamIds) {
      dependencies.push({ taskId: tQaId, dependsOnTaskId: upId });
    }

    return { tasks, dependencies };
  }
}
