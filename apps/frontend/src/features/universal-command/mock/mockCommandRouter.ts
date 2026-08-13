import { UniversalCommand, CommandSource } from '../types/command';
import { IntentClassification, IntentCategory } from '../types/intent';
import { ResolvedCapability } from '../types/capability';
import { CommandPermissionAssessment, CommandRiskLevel, CommandPolicy } from '../types/permission';
import { CommandPlan } from '../types/execution';

export class MockCommandRouter {
  classifyIntent(input: string): IntentClassification {
    const lower = input.toLowerCase();

    if (lower.includes('volume') || lower.includes('mute') || lower.includes('unmute') || lower.includes('louder') || lower.includes('quieter') || lower.includes('brightness') || lower.includes('wifi') || lower.includes('bluetooth') || lower.includes('ram') || lower.includes('cpu') || lower.includes('battery') || lower.includes('system info') || lower.includes('system status') || lower.includes('tasklist') || lower.includes('close') || lower.includes('terminate') || lower.includes('screenshot') || lower.includes('restart') || lower.includes('shutdown') || lower.includes('lock')) {
      let action = 'GET_SYSTEM_INFO';
      if (lower.includes('volume')) action = lower.includes('mute') ? 'MUTE_VOLUME' : 'SET_VOLUME';
      else if (lower.includes('brightness')) action = 'SET_BRIGHTNESS';
      else if (lower.includes('wifi')) action = 'SET_WIFI_STATE';
      else if (lower.includes('bluetooth')) action = 'SET_BLUETOOTH_STATE';
      else if (lower.includes('close') || lower.includes('terminate')) action = 'TERMINATE_PROCESS';
      else if (lower.includes('screenshot')) action = 'CAPTURE_SCREENSHOT';
      else if (lower.includes('lock')) action = 'POWER_LOCK';
      else if (lower.includes('restart')) action = 'POWER_RESTART';
      else if (lower.includes('shutdown')) action = 'POWER_SHUTDOWN';

      return { category: 'SYSTEM_CONTROL', confidence: 0.98, extractedTarget: input, extractedAction: action };
    }

    if (lower.includes('screen') || lower.includes('look at') || lower.includes('error') || lower.includes('see') || lower.includes('visual') || lower.includes('image') || lower.includes('button')) {
      return { category: 'VISION_ANALYSIS', confidence: 0.98, extractedTarget: 'Screen Frame', extractedAction: 'OBSERVE_SCREEN' };
    }
    if (lower.includes('youtube') || lower.includes('google') || lower.includes('github') || lower.includes('website') || lower.includes('webpage') || lower.includes('http') || lower.includes('www.') || lower.includes('search google') || lower.includes('search web')) {
      let action = 'NAVIGATE';
      if (lower.includes('search')) action = 'TYPE_TEXT';
      else if (lower.includes('read') || lower.includes('summarize')) action = 'READ_PAGE';
      else if (lower.includes('click')) action = 'CLICK_ELEMENT';

      return { category: 'FILE_OPERATION', confidence: 0.97, extractedTarget: input, extractedAction: action };
    }
    if (lower.includes('vs code') || lower.includes('chrome') || lower.includes('spotify') || lower.includes('open app')) {
      return { category: 'APPLICATION_CONTROL', confidence: 0.95, extractedTarget: 'Local Workstation', extractedAction: 'Launch Application' };
    }
    if (lower.includes('folder') || lower.includes('file') || lower.includes('pdf') || lower.includes('desktop') || lower.includes('downloads') || lower.includes('documents')) {
      let action = 'READ_DIRECTORY';
      if (lower.includes('create') || lower.includes('make')) action = lower.includes('file') ? 'CREATE_FILE' : 'CREATE_DIRECTORY';
      else if (lower.includes('find') || lower.includes('search')) action = 'SEARCH_FILES';
      else if (lower.includes('move')) action = 'MOVE_FILE';
      else if (lower.includes('copy')) action = 'COPY_FILE';
      else if (lower.includes('delete') || lower.includes('remove')) action = lower.includes('folder') ? 'DELETE_DIRECTORY' : 'DELETE_FILE';

      return { category: 'FILE_OPERATION', confidence: 0.96, extractedTarget: input, extractedAction: action };
    }
    if (lower.includes('light') || lower.includes('tv') || lower.includes('thermostat')) {
      return { category: 'SMART_HOME_CONTROL', confidence: 0.92, extractedTarget: 'Smart Home Mesh', extractedAction: 'Device Power Toggle' };
    }
    if (lower.includes('portfolio') || lower.includes('erp') || lower.includes('hospital')) {
      return { category: 'MISSION_REQUEST', confidence: 0.98, extractedTarget: 'Nova Mission Control', extractedAction: 'Orchestrate Mission' };
    }
    if (lower.includes('agent') || lower.includes('research') || lower.includes('architect')) {
      return { category: 'AGENT_TASK', confidence: 0.94, extractedTarget: 'Agent Workforce', extractedAction: 'Delegate Task' };
    }
    if (lower.includes('remember') || lower.includes('decide') || lower.includes('frontend')) {
      return { category: 'MEMORY_SEARCH', confidence: 0.91, extractedTarget: 'Vector Memory Store', extractedAction: 'Retrieve Memories' };
    }
    if (lower.includes('screenshot') || lower.includes('restart') || lower.includes('wifi')) {
      return { category: 'SYSTEM_CONTROL', confidence: 0.96, extractedTarget: 'Host OS Runtime', extractedAction: 'System Execution' };
    }

    return { category: 'CONVERSATION', confidence: 0.88, extractedAction: 'Natural Language Response' };
  }

  resolveCapability(category: IntentCategory): ResolvedCapability {
    const capabilityMap: Record<IntentCategory, ResolvedCapability> = {
      APPLICATION_CONTROL: { type: 'APPLICATION_CONTROL', providerDomain: 'device-control', name: 'Application Control', description: 'Launch & manage desktop applications', iconName: 'AppWindow' },
      SMART_HOME_CONTROL: { type: 'SMART_HOME', providerDomain: 'device-control', name: 'Smart Home Control', description: 'Control connected IoT & smart home devices', iconName: 'Lightbulb' },
      MISSION_REQUEST: { type: 'MISSION_ORCHESTRATOR', providerDomain: 'missions', name: 'Mission Orchestrator', description: 'Decompose complex goals into autonomous agent tasks', iconName: 'Rocket' },
      AGENT_TASK: { type: 'AGENT_WORKFORCE', providerDomain: 'agents', name: 'Agent Workforce', description: 'Delegate tasks to specialized AI agents', iconName: 'Bot' },
      MEMORY_SEARCH: { type: 'MEMORY_SYSTEM', providerDomain: 'memory', name: 'Memory System', description: 'Search episodic and semantic vector memories', iconName: 'Brain' },
      SYSTEM_CONTROL: { type: 'SYSTEM_CONTROL', providerDomain: 'device-control', name: 'System Control', description: 'Execute host OS system actions', iconName: 'Monitor' },
      CONVERSATION: { type: 'CONVERSATION_ENGINE', providerDomain: 'conversation', name: 'Nova Conversation Core', description: 'Interactive multi-modal conversation engine', iconName: 'Sparkles' },
      GENERAL_QUESTION: { type: 'CONVERSATION_ENGINE', providerDomain: 'conversation', name: 'Nova Conversation Core', description: 'Interactive multi-modal conversation engine', iconName: 'Sparkles' },
      RESEARCH: { type: 'RESEARCH_ENGINE', providerDomain: 'agents', name: 'Research Engine', description: 'Deep literature search & scientific synthesis', iconName: 'Search' },
      KNOWLEDGE_QUERY: { type: 'KNOWLEDGE_GRAPH', providerDomain: 'knowledge', name: 'Knowledge Graph', description: 'Query domain entities & relationships', iconName: 'Network' },
      CODE_TASK: { type: 'AGENT_WORKFORCE', providerDomain: 'agents', name: 'Code Intelligence', description: 'Analyze & refactor codebase', iconName: 'Code' },
      FILE_OPERATION: { type: 'FILE_SYSTEM', providerDomain: 'device-control', name: 'File System Engine', description: 'Search & organize files', iconName: 'Folder' },
      DEVICE_CONTROL: { type: 'DEVICE_CONTROL', providerDomain: 'device-control', name: 'Device Control Mesh', description: 'Manage connected devices', iconName: 'Laptop' },
      PHONE_CONTROL: { type: 'PHONE_CONTROL', providerDomain: 'device-control', name: 'Phone Control Engine', description: 'Manage mobile device operations', iconName: 'Smartphone' },
      AUTOMATION_REQUEST: { type: 'MISSION_ORCHESTRATOR', providerDomain: 'missions', name: 'Workflow Automation', description: 'Automate repetitive multi-step processes', iconName: 'Zap' },
      VISION_ANALYSIS: { type: 'VISION_ENGINE', providerDomain: 'conversation', name: 'Vision Engine', description: 'Analyze UI images & multimodal assets', iconName: 'Eye' },
      SETTINGS: { type: 'SYSTEM_CONTROL', providerDomain: 'device-control', name: 'System Settings', description: 'Configure system settings', iconName: 'Settings' },
      UNKNOWN: { type: 'CONVERSATION_ENGINE', providerDomain: 'conversation', name: 'Nova Core', description: 'Default conversation fallback', iconName: 'Sparkles' },
    };

    return capabilityMap[category] || capabilityMap.CONVERSATION;
  }

  assessPermission(input: string, category: IntentCategory): CommandPermissionAssessment {
    const lower = input.toLowerCase();
    let riskLevel: CommandRiskLevel = 'SAFE';
    let policy: CommandPolicy = 'ALLOW';
    let requiresApproval = false;

    if (lower.includes('delete') || lower.includes('restart') || lower.includes('shutdown')) {
      riskLevel = 'HIGH';
      policy = 'ALLOW_WITH_APPROVAL';
      requiresApproval = true;
    } else if (lower.includes('portfolio') || lower.includes('erp') || lower.includes('send')) {
      riskLevel = 'MEDIUM';
      policy = 'ALLOW';
    } else if (lower.includes('open') || lower.includes('turn on')) {
      riskLevel = 'LOW';
      policy = 'ALLOW';
    }

    return {
      riskLevel,
      policy,
      requiredCapability: category,
      scope: 'Local Environment',
      reason: requiresApproval ? 'Sensitive operation requires explicit user confirmation.' : 'Standard capability authorized.',
      requiresApproval,
    };
  }

  generatePlan(intent: IntentClassification): CommandPlan {
    if (intent.category === 'APPLICATION_CONTROL') {
      return {
        steps: [
          { id: '1', stepNumber: 1, title: 'Identify Target Device', description: 'Resolve target workstation in local subnet', status: 'COMPLETED' },
          { id: '2', stepNumber: 2, title: 'Check Application Path', description: 'Locate executable binary', status: 'COMPLETED' },
          { id: '3', stepNumber: 3, title: 'Launch Process', description: 'Execute launch sequence', status: 'PENDING' },
          { id: '4', stepNumber: 4, title: 'Verify Execution', description: 'Confirm window focus', status: 'PENDING' },
        ],
        estimatedDurationSeconds: 1.2,
      };
    }

    if (intent.category === 'MISSION_REQUEST') {
      return {
        steps: [
          { id: '1', stepNumber: 1, title: 'Decompose Objectives', description: 'Analyze requirements & target scope', status: 'COMPLETED' },
          { id: '2', stepNumber: 2, title: 'Assemble Agent Workforce', description: 'Select Solution Architect & Engineers', status: 'PENDING' },
          { id: '3', stepNumber: 3, title: 'Generate Task DAG', description: 'Construct task dependency graph', status: 'PENDING' },
          { id: '4', stepNumber: 4, title: 'Start Execution', description: 'Begin autonomous task cycle', status: 'PENDING' },
        ],
        estimatedDurationSeconds: 4.5,
      };
    }

    return {
      steps: [
        { id: '1', stepNumber: 1, title: 'Process Query', description: 'Synthesize context & compute response', status: 'PENDING' },
      ],
      estimatedDurationSeconds: 0.5,
    };
  }

  routeCommand(rawInput: string, source: CommandSource = 'TEXT'): UniversalCommand {
    const intent = this.classifyIntent(rawInput);
    const capability = this.resolveCapability(intent.category);
    const permission = this.assessPermission(rawInput, intent.category);
    const plan = this.generatePlan(intent);

    return {
      id: `cmd-${Date.now()}`,
      source,
      rawInput,
      timestamp: new Date().toLocaleTimeString(),
      intent,
      target: intent.extractedTarget || 'Nova Core Engine',
      capability,
      permission,
      plan,
      executionState: permission.requiresApproval ? 'AWAITING_APPROVAL' : 'UNDERSTANDING',
    };
  }
}
