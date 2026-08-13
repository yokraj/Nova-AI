import { MetricCardData, AgentInfo, NotificationItem, MemoryItem } from '@/types';

export interface SystemTelemetry {
  cpuUsage: number;
  cpuDetails: string;
  gpuUsage: number;
  gpuDetails: string;
  ramUsageGb: number;
  ramTotalGb: number;
  ramPercent: number;
  storageUsedGb: number;
  storageTotalGb: number;
  storagePercent: number;
  networkDownMbps: number;
  networkUpMbps: number;
  temperatureC: number;
  tempStatus: 'nominal' | 'elevated' | 'critical';
}

export interface MissionItem {
  id: string;
  title: string;
  category: 'Research' | 'Engineering' | 'Automation' | 'Security' | 'Documentation';
  status: 'running' | 'queued' | 'completed' | 'failed';
  progress: number;
  assignedAgents: number;
  elapsedTime: string;
  subtasksCompleted: number;
  subtasksTotal: number;
}

export interface MockDevice {
  id: string;
  name: string;
  type: 'Desktop' | 'Mobile' | 'Laptop' | 'Display' | 'IoT Hub';
  os: string;
  status: 'online' | 'offline' | 'connected' | 'attention';
  ip: string;
  specs: string;
  batteryPercent?: number;
  signalStrength?: string;
  lastActive: string;
}

export interface MockAutomation {
  id: string;
  name: string;
  trigger: string;
  status: 'active' | 'scheduled' | 'completed' | 'paused';
  lastRun: string;
  nextRun: string;
  executionCount: number;
  category: 'Routine' | 'Maintenance' | 'Monitoring' | 'Analytics';
}

export interface ActivityTimelineItem {
  id: string;
  title: string;
  description: string;
  category: 'agent' | 'memory' | 'security' | 'automation' | 'system';
  timestamp: string;
  icon: string;
}

export interface QuickActionItem {
  id: string;
  title: string;
  description: string;
  iconName: string;
  category: 'create' | 'run' | 'navigate';
  commandSuggestion?: string;
}

export const MOCK_TELEMETRY: SystemTelemetry = {
  cpuUsage: 24.5,
  cpuDetails: '4.2 GHz • 16 Cores / 32 Threads',
  gpuUsage: 42.0,
  gpuDetails: 'NVIDIA RTX 4090 • 18.2 GB VRAM',
  ramUsageGb: 16.2,
  ramTotalGb: 32.0,
  ramPercent: 50.6,
  storageUsedGb: 412.0,
  storageTotalGb: 1000.0,
  storagePercent: 41.2,
  networkDownMbps: 1250,
  networkUpMbps: 850,
  temperatureC: 48,
  tempStatus: 'nominal',
};

export const MOCK_ACTIVE_AGENTS_EXTENDED: (AgentInfo & {
  currentTask: string;
  progress: number;
  latencyMs: number;
  division: string;
})[] = [
  {
    id: 'agent-exec-1',
    name: 'Solution Architect',
    role: 'System Design & Blueprinting',
    status: 'active',
    tasksCompleted: 248,
    avatar: 'SA',
    currentTask: 'Designing microservice DAG for Hospital ERP',
    progress: 88,
    latencyMs: 14,
    division: 'Architecture Division',
  },
  {
    id: 'agent-eng-1',
    name: 'Backend Lead Agent',
    role: 'FastAPI / REST API Engine',
    status: 'busy',
    tasksCompleted: 512,
    avatar: 'BE',
    currentTask: 'Generating JWT OAuth2 & RBAC middleware',
    progress: 64,
    latencyMs: 18,
    division: 'Backend Division',
  },
  {
    id: 'agent-qa-1',
    name: 'QA & Security Reviewer',
    role: 'Automated Testing & Audit',
    status: 'active',
    tasksCompleted: 310,
    avatar: 'QA',
    currentTask: 'Running security vulnerability static audit',
    progress: 92,
    latencyMs: 11,
    division: 'Quality & Security',
  },
  {
    id: 'agent-res-1',
    name: 'Research Lead Agent',
    role: 'Knowledge Graph & Search',
    status: 'active',
    tasksCompleted: 429,
    avatar: 'RL',
    currentTask: 'Synthesizing arXiv literature on deep learning',
    progress: 75,
    latencyMs: 22,
    division: 'Research Division',
  },
  {
    id: 'agent-auto-1',
    name: 'Desktop Automation Agent',
    role: 'OS & GUI Orchestration',
    status: 'idle',
    tasksCompleted: 184,
    avatar: 'DA',
    currentTask: 'Waiting for voice macro execution signal',
    progress: 100,
    latencyMs: 8,
    division: 'Automation Division',
  },
  {
    id: 'agent-ui-1',
    name: 'UI/UX Design Agent',
    role: 'Design Tokens & Glassmorphism',
    status: 'active',
    tasksCompleted: 295,
    avatar: 'UX',
    currentTask: 'Generating responsive dashboard layout specs',
    progress: 95,
    latencyMs: 12,
    division: 'Creative Division',
  },
];

export const MOCK_MISSIONS: MissionItem[] = [
  {
    id: 'msn-101',
    title: 'Analyze Nova Monorepo Architecture',
    category: 'Engineering',
    status: 'running',
    progress: 78,
    assignedAgents: 4,
    elapsedTime: '12m 45s',
    subtasksCompleted: 7,
    subtasksTotal: 9,
  },
  {
    id: 'msn-102',
    title: 'Prepare Weekly Executive Briefing & Telemetry Report',
    category: 'Automation',
    status: 'running',
    progress: 42,
    assignedAgents: 2,
    elapsedTime: '04m 10s',
    subtasksCompleted: 3,
    subtasksTotal: 7,
  },
  {
    id: 'msn-103',
    title: 'Index Project Documentation into Semantic Vector Store',
    category: 'Research',
    status: 'queued',
    progress: 0,
    assignedAgents: 1,
    elapsedTime: '00m 00s',
    subtasksCompleted: 0,
    subtasksTotal: 5,
  },
  {
    id: 'msn-104',
    title: 'Audit Microservice RBAC & Token Security Controls',
    category: 'Security',
    status: 'completed',
    progress: 100,
    assignedAgents: 3,
    elapsedTime: '08m 15s',
    subtasksCompleted: 6,
    subtasksTotal: 6,
  },
  {
    id: 'msn-105',
    title: 'Deploy Containerized Microservice Topology to Docker',
    category: 'Engineering',
    status: 'completed',
    progress: 100,
    assignedAgents: 5,
    elapsedTime: '15m 30s',
    subtasksCompleted: 8,
    subtasksTotal: 8,
  },
];

export const MOCK_DEVICES: MockDevice[] = [
  {
    id: 'dev-1',
    name: 'Primary Workstation',
    type: 'Desktop',
    os: 'Windows 11 Enterprise (x64)',
    status: 'online',
    ip: '192.168.1.100 (Host)',
    specs: 'Core i9-14900K • RTX 4090 • 64GB DDR5',
    lastActive: 'Just now',
  },
  {
    id: 'dev-2',
    name: 'Galaxy S24 Ultra',
    type: 'Mobile',
    os: 'Android 14 (One UI 6.1)',
    status: 'online',
    ip: '192.168.1.142',
    specs: 'Snapdragon 8 Gen 3 • 12GB RAM',
    batteryPercent: 92,
    signalStrength: 'Wi-Fi 6E (1.2 Gbps)',
    lastActive: '1 min ago',
  },
  {
    id: 'dev-3',
    name: 'MacBook Pro M3 Max',
    type: 'Laptop',
    os: 'macOS Sonoma 14.5',
    status: 'offline',
    ip: '192.168.1.115',
    specs: 'M3 Max 16-Core • 48GB Unified',
    batteryPercent: 78,
    signalStrength: 'Disconnected',
    lastActive: '2 hours ago',
  },
  {
    id: 'dev-4',
    name: 'Office Wall Matrix TV',
    type: 'Display',
    os: 'Tizen OS 7.0',
    status: 'connected',
    ip: '192.168.1.201',
    specs: '75" 4K Quantum Dot • HDMI Passthrough',
    lastActive: 'Active Stream',
  },
  {
    id: 'dev-5',
    name: 'IoT Edge Controller',
    type: 'IoT Hub',
    os: 'Ubuntu Server 24.04 LTS',
    status: 'attention',
    ip: '192.168.1.250',
    specs: 'Raspberry Pi 5 8GB • Zigbee 3.0',
    lastActive: 'Warning: CPU Temp 74°C',
  },
];

export const MOCK_AUTOMATIONS: MockAutomation[] = [
  {
    id: 'auto-1',
    name: 'Morning Executive Briefing & Standup Routine',
    trigger: 'Schedule (Every Mon-Fri 08:00 AM)',
    status: 'active',
    lastRun: 'Today 08:00 AM',
    nextRun: 'Tomorrow 08:00 AM',
    executionCount: 142,
    category: 'Routine',
  },
  {
    id: 'auto-2',
    name: 'Automated Vector Memory & Database Backup',
    trigger: 'Schedule (Daily 02:00 AM)',
    status: 'scheduled',
    lastRun: 'Yesterday 02:00 AM',
    nextRun: 'Tonight 02:00 AM',
    executionCount: 365,
    category: 'Maintenance',
  },
  {
    id: 'auto-3',
    name: 'Continuous Repository Security & Lint Audit',
    trigger: 'Git Push Event & File Change',
    status: 'active',
    lastRun: '15 mins ago',
    nextRun: 'Continuous',
    executionCount: 890,
    category: 'Monitoring',
  },
  {
    id: 'auto-4',
    name: 'System Telemetry & VRAM Health Guard',
    trigger: 'Metric Threshold (>85% VRAM)',
    status: 'active',
    lastRun: '1 hour ago',
    nextRun: 'Always On',
    executionCount: 1240,
    category: 'Monitoring',
  },
];

export const MOCK_ACTIVITY_TIMELINE: ActivityTimelineItem[] = [
  {
    id: 'act-1',
    title: 'Research Agent completed literature synthesis',
    description: 'Extracted key benchmarks on microservice orchestration from 14 papers.',
    category: 'agent',
    timestamp: '2 mins ago',
    icon: 'Search',
  },
  {
    id: 'act-2',
    title: 'Nova indexed 124 workspace documents',
    description: 'Updated vector memory store with semantic embeddings for apps/backend.',
    category: 'memory',
    timestamp: '10 mins ago',
    icon: 'FileCheck',
  },
  {
    id: 'act-3',
    title: 'Memory Engine stored 18 semantic memories',
    description: 'Saved user preferences and architecture design choices.',
    category: 'memory',
    timestamp: '25 mins ago',
    icon: 'Brain',
  },
  {
    id: 'act-4',
    title: 'Repository Security Audit completed cleanly',
    description: '0 critical vulnerabilities found across 73 Python/TypeScript packages.',
    category: 'security',
    timestamp: '42 mins ago',
    icon: 'ShieldCheck',
  },
  {
    id: 'act-5',
    title: 'Automation Workflow "Morning Standup" executed',
    description: 'Generated daily summary report and pushed notification to desktop tray.',
    category: 'automation',
    timestamp: '1 hour ago',
    icon: 'Workflow',
  },
];

export const MOCK_QUICK_ACTIONS: QuickActionItem[] = [
  {
    id: 'qa-1',
    title: 'New Chat',
    description: 'Start a natural conversation with Nova AI',
    iconName: 'MessageSquarePlus',
    category: 'create',
    commandSuggestion: 'Start a conversation about AI architecture',
  },
  {
    id: 'qa-2',
    title: 'Voice Command',
    description: 'Activate hands-free voice mode',
    iconName: 'Mic',
    category: 'run',
    commandSuggestion: 'Hey Nova, summarize my recent activity',
  },
  {
    id: 'qa-3',
    title: 'Deep Research',
    description: 'Search literature & index topics',
    iconName: 'Search',
    category: 'create',
    commandSuggestion: 'Research FastAPI vs Go microservices performance',
  },
  {
    id: 'qa-4',
    title: 'Create Document',
    description: 'Generate spec or technical doc',
    iconName: 'FileText',
    category: 'create',
    commandSuggestion: 'Create SRS documentation for ERP system',
  },
  {
    id: 'qa-5',
    title: 'Analyze File',
    description: 'Inspect code, image, or PDF file',
    iconName: 'FileSearch',
    category: 'run',
    commandSuggestion: 'Analyze codebase performance bottlenecks',
  },
  {
    id: 'qa-6',
    title: 'Run Mission',
    description: 'Launch autonomous multi-agent mission',
    iconName: 'Play',
    category: 'run',
    commandSuggestion: 'Build a Hospital Management System with React and PostgreSQL',
  },
  {
    id: 'qa-7',
    title: 'Open Terminal',
    description: 'Launch interactive terminal console',
    iconName: 'Terminal',
    category: 'navigate',
    commandSuggestion: 'Open terminal and check git status',
  },
  {
    id: 'qa-8',
    title: 'Manage Agents',
    description: 'Configure 67-agent workforce',
    iconName: 'Users',
    category: 'navigate',
    commandSuggestion: 'View active workforce status and divisions',
  },
  {
    id: 'qa-9',
    title: 'Memory Search',
    description: 'Query semantic vector memory',
    iconName: 'Brain',
    category: 'run',
    commandSuggestion: 'Search memory for user preferences and project history',
  },
  {
    id: 'qa-10',
    title: 'Knowledge Graph',
    description: 'Explore entity relationships',
    iconName: 'Network',
    category: 'navigate',
    commandSuggestion: 'Explore knowledge graph for architecture components',
  },
  {
    id: 'qa-11',
    title: 'Device Mesh',
    description: 'Orchestrate cross-platform devices',
    iconName: 'Laptop',
    category: 'navigate',
    commandSuggestion: 'Check multi-device mesh connection status',
  },
  {
    id: 'qa-12',
    title: 'Automation Studio',
    description: 'No-code workflow recorder',
    iconName: 'Workflow',
    category: 'create',
    commandSuggestion: 'Run my morning standup automation routine',
  },
];

export const MOCK_ANALYTICS_SERIES = {
  aiRequestsOverTime: [
    { time: '08:00', requests: 120, latency: 14 },
    { time: '10:00', requests: 450, latency: 12 },
    { time: '12:00', requests: 890, latency: 16 },
    { time: '14:00', requests: 1240, latency: 11 },
    { time: '16:00', requests: 980, latency: 13 },
    { time: '18:00', requests: 1560, latency: 15 },
    { time: '20:00', requests: 820, latency: 10 },
  ],
  agentActivityDistribution: [
    { name: 'Architecture', tasks: 248 },
    { name: 'Backend', tasks: 512 },
    { name: 'Research', tasks: 429 },
    { name: 'Testing/QA', tasks: 310 },
    { name: 'UI/UX', tasks: 295 },
    { name: 'DevOps', tasks: 184 },
  ],
  memoryGrowth: [
    { day: 'Mon', memories: 128000, entities: 10200 },
    { day: 'Tue', memories: 132500, entities: 10800 },
    { day: 'Wed', memories: 136200, entities: 11400 },
    { day: 'Thu', memories: 139800, entities: 11900 },
    { day: 'Fri', memories: 142850, entities: 12480 },
  ],
};
