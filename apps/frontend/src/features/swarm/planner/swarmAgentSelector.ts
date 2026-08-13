import { SwarmAgent } from '../types/swarm';

export class SwarmAgentSelector {
  private availableRoster: SwarmAgent[] = [
    {
      agentId: 'agent-arch-01',
      name: 'System Architecture Agent',
      domain: 'Planning',
      capabilities: ['Architecture Analysis', 'DAG Planning', 'System Design'],
      tools: ['filesystem.read_directory', 'filesystem.read_file', 'system.get_info'],
      workload: 10,
      isAvailable: true,
    },
    {
      agentId: 'agent-sec-02',
      name: 'Security Guard Agent',
      domain: 'Security',
      capabilities: ['Vulnerability Scan', 'Policy Enforcement', 'Permission Audit'],
      tools: ['filesystem.read_file', 'system.process_list'],
      workload: 5,
      isAvailable: true,
    },
    {
      agentId: 'agent-qa-03',
      name: 'QA & Testing Agent',
      domain: 'Testing',
      capabilities: ['Unit Testing', 'Verification Check', 'State Audit'],
      tools: ['filesystem.read_file', 'application.verify_running', 'system.process_find'],
      workload: 0,
      isAvailable: true,
    },
    {
      agentId: 'agent-ops-04',
      name: 'DevOps & System Automation Agent',
      domain: 'System Operations',
      capabilities: ['Process Launch', 'Directory Provisioning', 'Deployment Prep'],
      tools: ['filesystem.create_directory', 'filesystem.write_file', 'application.open', 'system.volume_set'],
      workload: 15,
      isAvailable: true,
    },
    {
      agentId: 'agent-vis-05',
      name: 'Vision & Screen Intelligence Agent',
      domain: 'Analysis',
      capabilities: ['Screen Capture', 'Visual OCR', 'UI Inspection'],
      tools: ['vision.observe_screen', 'system.screenshot_capture'],
      workload: 0,
      isAvailable: true,
    },
  ];

  selectAgentsForGoal(goal: string): SwarmAgent[] {
    const lowerGoal = goal.toLowerCase();
    const selectedMap = new Map<string, SwarmAgent>();

    // Mandatory Lead Planner
    selectedMap.set('agent-arch-01', this.availableRoster[0]);

    if (lowerGoal.includes('folder') || lowerGoal.includes('file') || lowerGoal.includes('create') || lowerGoal.includes('deploy') || lowerGoal.includes('app') || lowerGoal.includes('volume')) {
      selectedMap.set('agent-ops-04', this.availableRoster[3]);
    }

    if (lowerGoal.includes('security') || lowerGoal.includes('permission') || lowerGoal.includes('scan') || lowerGoal.includes('deploy') || lowerGoal.includes('vulnerability')) {
      selectedMap.set('agent-sec-02', this.availableRoster[1]);
    }

    if (lowerGoal.includes('test') || lowerGoal.includes('verify') || lowerGoal.includes('qa') || lowerGoal.includes('check') || lowerGoal.includes('deploy')) {
      selectedMap.set('agent-qa-03', this.availableRoster[2]);
    }

    if (lowerGoal.includes('screen') || lowerGoal.includes('look') || lowerGoal.includes('vision') || lowerGoal.includes('screenshot')) {
      selectedMap.set('agent-vis-05', this.availableRoster[4]);
    }

    return Array.from(selectedMap.values());
  }
}
